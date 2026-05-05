import os
import shutil
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.models.meal import FoodPhoto, MealEntry, DetectedFoodItem
from app.routers.auth import get_current_user
from app.schemas.meal import (
    MealPhotoResponse,
    MealRead,
    CaloriesDayResponse,
    MealCorrection,
)
from app.services.ai_food_service import recognize_food_from_photo


router = APIRouter(
    prefix="/meals",
    tags=["Meals"]
)


UPLOAD_DIR = "uploads"

def get_today_period():
    now = datetime.utcnow()

    start_of_day = datetime(
        year=now.year,
        month=now.month,
        day=now.day
    )

    end_of_day = start_of_day + timedelta(days=1)

    return start_of_day, end_of_day

@router.post("/photo", response_model=MealPhotoResponse)
def upload_meal_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только изображения"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]

    unique_filename = f"{uuid4()}{file_extension}"

    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    food_photo = FoodPhoto(
        user_id=current_user.id,
        file_path=file_path
    )

    session.add(food_photo)
    session.commit()
    session.refresh(food_photo)

    ai_result = recognize_food_from_photo(file_path)

    total_calories = sum(item["calories"] for item in ai_result)

    meal_entry = MealEntry(
        user_id=current_user.id,
        photo_id=food_photo.id,
        total_calories=total_calories
    )

    session.add(meal_entry)
    session.commit()
    session.refresh(meal_entry)

    detected_items = []

    for item in ai_result:
        detected_item = DetectedFoodItem(
            meal_id=meal_entry.id,
            name=item["name"],
            calories=item["calories"],
            protein=item["protein"],
            fat=item["fat"],
            carbs=item["carbs"],
            confidence=item["confidence"]
        )

        session.add(detected_item)
        detected_items.append(detected_item)

    session.commit()

    return {
        "meal_id": meal_entry.id,
        "photo_id": food_photo.id,
        "items": ai_result,
        "total_calories": total_calories
    }




@router.get("/day", response_model=list[MealRead])
def get_meals_for_today(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    start_of_day, end_of_day = get_today_period()

    statement = (
        select(MealEntry)
        .where(MealEntry.user_id == current_user.id)
        .where(MealEntry.created_at >= start_of_day)
        .where(MealEntry.created_at < end_of_day)
    )

    meals = session.exec(statement).all()

    result = []

    for meal in meals:
        items_statement = select(DetectedFoodItem).where(
            DetectedFoodItem.meal_id == meal.id
        )

        items = session.exec(items_statement).all()

        result.append(
            {
                "id": meal.id,
                "photo_id": meal.photo_id,
                "total_calories": meal.total_calories,
                "created_at": meal.created_at,
                "items": items
            }
        )

    return result


@router.get("/calories/day", response_model=CaloriesDayResponse)
def get_calories_for_today(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    start_of_day, end_of_day = get_today_period()

    statement = (
        select(MealEntry)
        .where(MealEntry.user_id == current_user.id)
        .where(MealEntry.created_at >= start_of_day)
        .where(MealEntry.created_at < end_of_day)
    )

    meals = session.exec(statement).all()

    total_calories = sum(meal.total_calories for meal in meals)

    return {
        "date": start_of_day.date().isoformat(),
        "total_calories": total_calories,
        "meals_count": len(meals)
    }

@router.patch("/{meal_id}", response_model=MealRead)
def correct_meal_result(
    meal_id: int,
    correction_data: MealCorrection,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = (
        select(MealEntry)
        .where(MealEntry.id == meal_id)
        .where(MealEntry.user_id == current_user.id)
    )

    meal = session.exec(statement).first()

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись питания не найдена"
        )

    items_statement = select(DetectedFoodItem).where(
        DetectedFoodItem.meal_id == meal.id
    )

    items = session.exec(items_statement).all()

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Распознанные продукты не найдены"
        )

    # Сейчас у нас fake AI возвращает только один продукт.
    # Поэтому исправляем первый продукт.
    item = items[0]

    update_data = correction_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(item, field, value)

    session.add(item)
    session.commit()
    session.refresh(item)

    # После исправления пересчитываем калории приёма пищи.
    updated_items = session.exec(items_statement).all()
    meal.total_calories = sum(food_item.calories for food_item in updated_items)

    session.add(meal)
    session.commit()
    session.refresh(meal)

    return {
        "id": meal.id,
        "photo_id": meal.photo_id,
        "total_calories": meal.total_calories,
        "created_at": meal.created_at,
        "items": updated_items
    }
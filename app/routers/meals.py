import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.models.meal import FoodPhoto, MealEntry, DetectedFoodItem
from app.routers.auth import get_current_user
from app.schemas.meal import MealPhotoResponse
from app.services.ai_food_service import recognize_food_from_photo


router = APIRouter(
    prefix="/meals",
    tags=["Meals"]
)


UPLOAD_DIR = "uploads"


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
            carbs=item["carbs"]
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
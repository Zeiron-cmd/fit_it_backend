from datetime import datetime

from pydantic import BaseModel


class FoodItemRead(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float


class MealPhotoResponse(BaseModel):
    meal_id: int
    photo_id: int
    items: list[FoodItemRead]
    total_calories: float


class MealRead(BaseModel):
    id: int
    photo_id: int | None = None
    total_calories: float
    created_at: datetime
    items: list[FoodItemRead]


class CaloriesDayResponse(BaseModel):
    date: str
    total_calories: float
    meals_count: int
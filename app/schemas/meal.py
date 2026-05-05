from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FoodItemRead(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float
    confidence: float


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


class MealCorrection(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    confidence: Optional[float] = None
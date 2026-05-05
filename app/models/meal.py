from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class FoodPhoto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")

    file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MealEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    photo_id: Optional[int] = Field(default=None, foreign_key="foodphoto.id")

    total_calories: float = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)


class DetectedFoodItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    meal_id: int = Field(foreign_key="mealentry.id")

    name: str
    calories: float
    protein: float
    fat: float
    carbs: float

    confidence: float = 0.0
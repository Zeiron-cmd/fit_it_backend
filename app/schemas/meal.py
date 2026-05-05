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
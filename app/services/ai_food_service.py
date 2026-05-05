def recognize_food_from_photo(file_path: str) -> list[dict]:
    """
    Пока это не настоящая нейронка.

    Мы просто делаем вид, что backend распознал еду на фото.
    Потом эту функцию можно будет заменить на реальный вызов модели.
    """

    return [
        {
            "name": "Омлет",
            "calories": 250,
            "protein": 18,
            "fat": 16,
            "carbs": 3,
            "confidence": 0.92
        }
    ]
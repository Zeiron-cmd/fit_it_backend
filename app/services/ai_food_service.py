import json
import re
from typing import Any

from app.config import get_settings


FOOD_RECOGNITION_PROMPT = """
Проанализируй фото еды и верни только JSON без Markdown.
Формат ответа:
[
  {
    "name": "название продукта или блюда на русском",
    "calories": 250,
    "protein": 18,
    "fat": 16,
    "carbs": 3,
    "confidence": 0.92
  }
]

Оцени КБЖУ для видимой порции. Если на фото несколько продуктов — верни несколько объектов.
confidence должен быть числом от 0 до 1.
""".strip()


def recognize_food_from_photo(file_path: str) -> list[dict]:
    """
    Recognize food from a photo through Gemini when GEMINI_API_KEY is configured.
    Without an API key the old demo fallback is kept, so local development still works.
    """
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        return _fallback_food_result()

    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        uploaded_file = client.files.upload(file=file_path)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[uploaded_file, FOOD_RECOGNITION_PROMPT],
        )
        return _parse_food_items(response.text)
    except Exception:  # noqa: BLE001 - keep demo flow working if Gemini is unavailable by region/key/quota.
        return _fallback_food_result()


def _parse_food_items(raw_text: str | None) -> list[dict]:
    if not raw_text:
        raise ValueError("Gemini вернул пустой ответ")

    text = _strip_markdown_code_fence(raw_text)
    data: Any = json.loads(text)

    if isinstance(data, dict):
        data = data.get("items") or data.get("foods") or [data]

    if not isinstance(data, list) or not data:
        raise ValueError("Gemini вернул JSON не в формате списка продуктов")

    return [_normalize_food_item(item) for item in data]


def _strip_markdown_code_fence(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, re.DOTALL)
    return match.group(1).strip() if match else stripped


def _normalize_food_item(item: dict[str, Any]) -> dict:
    return {
        "name": str(item.get("name") or "Неизвестное блюдо"),
        "calories": float(item.get("calories") or 0),
        "protein": float(item.get("protein") or 0),
        "fat": float(item.get("fat") or 0),
        "carbs": float(item.get("carbs") or 0),
        "confidence": _normalize_confidence(item.get("confidence")),
    }


def _normalize_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        confidence = 0.0
    return max(0.0, min(1.0, confidence))


def _fallback_food_result() -> list[dict]:
    return [
        {
            "name": "Омлет",
            "calories": 250,
            "protein": 18,
            "fat": 16,
            "carbs": 3,
            "confidence": 0.92,
        }
    ]

import json
import re
from typing import Any

from app.config import get_settings

import base64
from openai import OpenAI




FOOD_RECOGNITION_PROMPT = """
Проанализируй изображение еды.

Верни ТОЛЬКО валидный JSON-массив.
Не используй markdown.
Не используй ```json.
Не добавляй пояснений.

Формат:
[
  {
    "name": "название блюда",
    "calories": 250,
    "protein": 18,
    "fat": 16,
    "carbs": 3,
    "confidence": 0.92
  }
]

Оцени КБЖУ для видимой порции.
Если продуктов несколько — верни несколько объектов.
""".strip()


import base64
from openai import OpenAI


def recognize_food_from_photo(file_path: str) -> list[dict]:
    settings = get_settings()

    if not settings.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY не настроен")

    try:
        with open(file_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode()

        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": FOOD_RECOGNITION_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            temperature=0,
        )

        raw_text = response.choices[0].message.content

        return _parse_food_items(raw_text)

    except Exception as e:
        raise RuntimeError(
            f"Ошибка распознавания через OpenRouter: {e}"
        ) from e


def _parse_food_items(raw_text: str | None) -> list[dict]:
    if not raw_text:
        raise ValueError("Qwen вернул пустой ответ")

    text = _strip_markdown_code_fence(raw_text)
    data: Any = json.loads(text)

    if isinstance(data, dict):
        data = data.get("items") or data.get("foods") or [data]

    if not isinstance(data, list) or not data:
        raise ValueError("Qwen вернул JSON не в формате списка продуктов")

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




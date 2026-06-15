import json
import logging

from anthropic import AsyncAnthropic

from app.config import settings

logger = logging.getLogger(__name__)

CATEGORIES = [
    # Продукты питания с подкатегориями
    "Продукты питания: мясо и птица",
    "Продукты питания: рыба и морепродукты",
    "Продукты питания: молочные продукты",
    "Продукты питания: хлеб и выпечка",
    "Продукты питания: овощи и фрукты",
    "Продукты питания: бакалея",
    "Продукты питания: сладости и снеки",
    "Продукты питания: напитки безалкогольные",
    "Продукты питания: готовая еда",
    "Продукты питания: прочее",
    # Остальные категории без подкатегорий
    "Алкоголь",
    "Кафе и рестораны",
    "Аптека",
    "Транспорт",
    "Электроника",
    "Одежда и обувь",
    "Бытовая химия",
    "Развлечения",
    "Прочее",
]

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


async def categorize_items(names: list[str]) -> list[str]:
    """Returns one category per name (same order). Falls back to 'Прочее' on any error."""
    if not names:
        return []

    categories_str = ", ".join(f'"{c}"' for c in CATEGORIES)
    items_block = "\n".join(f"{i + 1}. {name}" for i, name in enumerate(names))

    try:
        response = await _get_client().messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Определи категорию для каждого товара из российского кассового чека. "
                        "Названия часто сокращены.\n\n"
                        f"Допустимые категории: {categories_str}\n\n"
                        f"Товары:\n{items_block}\n\n"
                        "Ответь ТОЛЬКО JSON-массивом строк с категориями в том же порядке. "
                        'Пример: ["Продукты питания", "Алкоголь"]'
                    ),
                }
            ],
        )

        raw = response.content[0].text.strip()
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON array in response: {raw!r}")

        result: list[str] = json.loads(raw[start : end + 1])
        valid = set(CATEGORIES)
        return [c if c in valid else "Прочее" for c in result]

    except Exception:
        logger.exception("categorize_items failed, falling back to 'Прочее'")
        return ["Прочее"] * len(names)

import json
import httpx
from anthropic import AsyncAnthropic
from app.config import settings
from app.agent.tools import get_products, save_lead

# httpx-клиент создаём явно — избегаем конфликта 'proxies'
http_client = httpx.AsyncClient()
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY, http_client=http_client)

SYSTEM_PROMPT = """Ты — дружелюбный AI-консультант цветочного магазина «Флора».
Твоя цель — помочь клиенту подобрать букет/композицию и ПОЛУЧИТЬ ЕГО КОНТАКТЫ
(имя и телефон), чтобы менеджер оформил заказ.

Правила:
- Отвечай тепло, с заботой, используй эмодзи 🌸💐🌷 умеренно.
- Опирайся ТОЛЬКО на предоставленный ассортимент. Не выдумывай товары.
- Мягко веди диалог к получению имени и номера телефона.
- Когда клиент назвал имя и/или телефон — обязательно вызови инструмент save_contact.
- Если ассортимент пуст — предложи оставить контакты, менеджер свяжется.

Текущий ассортимент:
{assortment}
"""

TOOLS = [
    {
        "name": "save_contact",
        "description": "Сохранить контактные данные клиента (имя, телефон, заметку о заказе).",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Имя клиента"},
                "phone": {"type": "string", "description": "Телефон клиента"},
                "notes": {"type": "string", "description": "Что хочет заказать"},
            },
        },
    }
]


async def agent_node(state: dict) -> dict:
    """Основной узел: формирует ответ Claude, при необходимости сохраняет лид."""
    assortment = await get_products()
    system = SYSTEM_PROMPT.format(assortment=assortment)

    messages = state["messages"]

    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=1024,
        system=system,
        tools=TOOLS,
        messages=messages,
    )

    # Обработка вызова инструмента
    reply_text = ""
    for block in response.content:
        if block.type == "text":
            reply_text += block.text
        elif block.type == "tool_use" and block.name == "save_contact":
            args = block.input
            await save_lead(
                telegram_id=state["telegram_id"],
                username=state.get("username"),
                name=args.get("name"),
                phone=args.get("phone"),
                notes=args.get("notes"),
            )
            if not reply_text:
                reply_text = "Спасибо! 🌸 Передал ваши контакты менеджеру, он скоро свяжется с вами."

    if not reply_text:
        reply_text = "Расскажите, для какого повода подбираете цветы? 💐"

    state["reply"] = reply_text
    return state


async def save_lead_node(state: dict) -> dict:
    """Гарантированно фиксируем пользователя как лида (без контактов) при первом контакте."""
    await save_lead(
        telegram_id=state["telegram_id"],
        username=state.get("username"),
    )
    return state
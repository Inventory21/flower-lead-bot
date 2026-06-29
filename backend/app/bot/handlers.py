from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message as TgMessage
from sqlalchemy import select
from app.agent.graph import graph
from app.database import async_session
from app.models import Message

router = Router()


async def load_history(telegram_id: int, limit: int = 10) -> list:
    async with async_session() as s:
        res = await s.execute(
            select(Message)
            .where(Message.telegram_id == telegram_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        msgs = list(reversed(res.scalars().all()))
        return [{"role": m.role, "content": m.content} for m in msgs]


async def save_message(telegram_id: int, role: str, content: str):
    async with async_session() as s:
        s.add(Message(telegram_id=telegram_id, role=role, content=content))
        await s.commit()


@router.message(CommandStart())
async def start(message: TgMessage):
    await message.answer(
        "Здравствуйте! 🌸 Я консультант цветочного магазина «Флора».\n"
        "Помогу подобрать идеальный букет. Для какого повода ищете цветы? 💐"
    )


@router.message()
async def handle_message(message: TgMessage):
    tg_id = message.from_user.id
    username = message.from_user.username
    text = message.text or ""

    await save_message(tg_id, "user", text)
    history = await load_history(tg_id)

    result = await graph.ainvoke({
        "telegram_id": tg_id,
        "username": username,
        "messages": history,
    })

    reply = result["reply"]
    await save_message(tg_id, "assistant", reply)
    await message.answer(reply)
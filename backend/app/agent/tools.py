from sqlalchemy import select
from app.database import async_session
from app.models import Product, Lead


async def get_products() -> str:
    """Возвращает текущий ассортимент для контекста модели."""
    async with async_session() as s:
        res = await s.execute(select(Product).order_by(Product.category))
        products = res.scalars().all()
        if not products:
            return "Ассортимент пока пуст."
        lines = []
        for p in products:
            price = f"{p.price} ₽" if p.price else "цена по запросу"
            cat = f"[{p.category}] " if p.category else ""
            desc = f" — {p.description}" if p.description else ""
            lines.append(f"{cat}{p.name}: {price}{desc}")
        return "\n".join(lines)


async def save_lead(telegram_id: int, username: str | None,
                    name: str | None = None, phone: str | None = None,
                    notes: str | None = None):
    """Создаёт или обновляет лида."""
    async with async_session() as s:
        res = await s.execute(select(Lead).where(Lead.telegram_id == telegram_id))
        lead = res.scalar_one_or_none()
        if lead:
            if name: lead.name = name
            if phone: lead.phone = phone
            if username: lead.username = username
            if notes: lead.notes = notes
        else:
            lead = Lead(telegram_id=telegram_id, username=username,
                        name=name, phone=phone, notes=notes)
            s.add(lead)
        await s.commit()
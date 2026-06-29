import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import settings
from app.database import init_db
from app.bot.handlers import router

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
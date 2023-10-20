import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from database.Database import Database as db
from log import logger, start_log
from handlers.handlers import reg_handlers
from dotenv import load_dotenv


def reg_all_handlers(dp):
    reg_handlers(dp)

async def main():
    start_log()
    logger.info("Starting bot")

    storage = MemoryStorage()
    load_dotenv()
    bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(LoggingMiddleware())

    # Ловим сообщения
    reg_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        # Остановили бота и закрываем сессию
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


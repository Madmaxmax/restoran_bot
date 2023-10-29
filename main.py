import asyncio
import multiprocessing
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from log import logger, start_log
from handlers.handlers import reg_handlers
from dotenv import load_dotenv
from flask_function.function import start_flask_app


def reg_all_handlers(dp):
    reg_handlers(dp)


load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)


async def start_aiogram_bot():
    start_log()
    logger.info("Starting bot")

    storage = MemoryStorage()

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


def run_bot():
    asyncio.run(start_aiogram_bot())


if __name__ == "__main__":
    processes = []
    process1 = multiprocessing.Process(target=run_bot)
    processes.append(process1)
    process1.start()
    process2 = multiprocessing.Process(target=start_flask_app)
    processes.append(process2)
    process2.start()

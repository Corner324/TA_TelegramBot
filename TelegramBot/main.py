import asyncio
import logging
import os

from handlers import setup_handlers

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.fsm.storage.redis import RedisStorage

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
# Используем Redis для хранения состояний FSM
storage = RedisStorage.from_url(os.getenv("REDIS_DSN", "redis://localhost:6379/0"))
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)


async def main():
    # Регистрируем все обработчики
    setup_handlers(dp)

    logger.info("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

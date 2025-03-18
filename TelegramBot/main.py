import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
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


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! Добро пожаловать в нашего бота. Ожидайте дальнейших функций!"
    )


async def main():
    logger.info("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

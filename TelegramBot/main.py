import asyncio
import logging
import os

from handlers import setup_handlers
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from aiogram.fsm.storage.redis import RedisStorage

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Используем Redis для хранения состояний FSM
storage = RedisStorage.from_url(os.getenv("REDIS_DSN", "redis://localhost:6379/0"))
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

async def set_bot_commands(bot: Bot):
    """Настройка команд в меню Telegram"""
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/catalog", description="Посмотреть каталог"),
        BotCommand(command="/faq", description="Частые вопросы"),
        BotCommand(command="/cart", description="Открыть корзину"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды меню Telegram успешно настроены")

async def main():
    setup_handlers(dp)
    
    await set_bot_commands(bot)

    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import os
from dotenv import load_dotenv

load_dotenv()

# Базовые настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_DSN = os.getenv("REDIS_DSN", "redis://redis:6379/0")

# Настройки подключения к базе данных
DB_HOST = os.getenv("DATABASE_HOST", "db")
DB_PORT = os.getenv("BACKEND_DATABASE_PORT", "5432")
DB_NAME = os.getenv("BACKEND_DATABASE_NAME")
DB_USER = os.getenv("BACKEND_DATABASE_USER")
DB_PASS = os.getenv("BACKEND_DATABASE_PASSWORD")

# URL для подключения к базе данных
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Настройки для проверки подписки
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID")
REQUIRED_GROUP_ID = os.getenv("REQUIRED_GROUP_ID")

# Настройки платежных систем
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

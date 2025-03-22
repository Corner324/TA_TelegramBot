# handlers.py
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import aiohttp
from utils.subscription_check import check_subscription
from config import REQUIRED_GROUP_URL, REQUIRED_CHANNEL_URL

router = Router()
logger = logging.getLogger(__name__)

API_URL = "http://backend_api:8000/api/users/register/"

@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    telegram_id = message.from_user.id
    is_subscribed = await check_subscription(bot, telegram_id)
    if not is_subscribed:
        kb = InlineKeyboardBuilder()
        kb.button(text="Подписаться на канал", url=f"https://t.me/{REQUIRED_GROUP_URL}")
        kb.button(text="Подписаться на группу", url=f"https://t.me/{REQUIRED_CHANNEL_URL}")
        kb.button(text="Проверить подписку", callback_data="check_subscription")
        kb.adjust(2, 1)
        await message.answer(
            "👋 Привет! Для использования бота необходимо подписаться на наш канал и группу.\n"
            "После подписки нажмите кнопку 'Проверить подписку'.",
            reply_markup=kb.as_markup(),
        )
        return

    # Проверяем регистрацию перед показом меню
    is_registered = await check_registration(telegram_id)
    if not is_registered:
        await register_user(telegram_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)
    await message.answer(
        f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        "Выберите действие в нашем магазине:",
        reply_markup=kb.as_markup(),
    )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot):
    telegram_id = callback.from_user.id
    is_subscribed = await check_subscription(bot, telegram_id)
    if not is_subscribed:
        await callback.answer("Вы всё ещё не подписаны на все необходимые каналы", show_alert=True)
        return

    # Проверяем регистрацию перед показом меню
    is_registered = await check_registration(telegram_id)
    if not is_registered:
        await register_user(telegram_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)
    await callback.message.edit_text(
        f"✅ Спасибо за подписку, {callback.from_user.first_name}!\n\n"
        "Выберите действие в нашем магазине:",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()

async def register_user(telegram_id: int):
    """Регистрация пользователя в Django API"""
    async with aiohttp.ClientSession() as session:
        payload = {"telegram_id": str(telegram_id)}
        try:
            async with session.post(API_URL, json=payload) as response:
                if response.status in (200, 201):
                    logger.info(f"Пользователь {telegram_id} успешно зарегистрирован или уже существует")
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка регистрации {telegram_id}: {error_text}")
        except Exception as e:
            logger.error(f"Исключение при регистрации {telegram_id}: {e}")

async def check_registration(telegram_id: int) -> bool:
    """Проверка, зарегистрирован ли пользователь"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json={"telegram_id": str(telegram_id)}) as response:
                return response.status == 200  # 200 означает, что пользователь уже существует
        except Exception as e:
            logger.error(f"Ошибка проверки регистрации {telegram_id}: {e}")
            return False

def register_handlers(dp):
    dp.include_router(router)
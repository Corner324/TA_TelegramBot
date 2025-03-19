from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from utils.subscription_check import check_subscription
from config import REQUIRED_CHANNEL_ID, REQUIRED_GROUP_URL

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    """Обработчик команды /start"""
    # Проверяем подписку на необходимые каналы
    is_subscribed = await check_subscription(bot, message.from_user.id)

    if not is_subscribed:
        # Пользователь не подписан на необходимые каналы/группы
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Подписаться на канал",
            url=f"https://t.me/c/{str(REQUIRED_CHANNEL_ID).replace('-100', '')}",
        )
        kb.button(
            text="Подписаться на группу", url=f"https://t.me/{REQUIRED_GROUP_URL}"
        )
        kb.button(text="Проверить подписку", callback_data="check_subscription")
        kb.adjust(2, 1)

        await message.answer(
            "👋 Привет! Для использования бота необходимо подписаться на наш канал и группу.\n"
            "После подписки нажмите кнопку 'Проверить подписку'.",
            reply_markup=kb.as_markup(),
        )
        return

    # Если пользователь подписан, показываем основное меню
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
    """Обработчик нажатия на кнопку проверки подписки"""
    is_subscribed = await check_subscription(bot, callback.from_user.id)

    if not is_subscribed:
        await callback.answer(
            "Вы всё ещё не подписаны на все необходимые каналы", show_alert=True
        )
        return

    # Если пользователь подписан, показываем основное меню
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


def register_handlers(dp):
    dp.include_router(router)

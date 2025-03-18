from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.subscription_check import check_subscription

router = Router()


def register_handlers(dp):
    dp.include_router(router)


@router.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды /start"""
    # Проверяем подписку на необходимые каналы
    is_subscribed = True
    # is_subscribed = await check_subscription(message.from_user.id) # Ожидаю подтверждения на создание группы и канала 

    if not is_subscribed:
        kb = InlineKeyboardBuilder()
        kb.button(text="Проверить подписку", callback_data="check_subscription")

        await message.answer(
            "Для использования бота необходимо подписаться на наш канал и группу.\n"
            "После подписки нажмите кнопку 'Проверить подписку'.",
            reply_markup=kb.as_markup(),
        )
        return

    # Пользователь подписан
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)

    await message.answer(
        "Добро пожаловать в наш магазин! Выберите действие:",
        reply_markup=kb.as_markup(),
    )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    """Обработчик нажатия на кнопку проверки подписки"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.answer(
            "Вы все еще не подписаны на все необходимые каналы", show_alert=True
        )
        return

    # Основное меню
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)

    await callback.message.edit_text(
        "Спасибо за подписку! Теперь вы можете пользоваться ботом.\n\n"
        "Выберите действие:",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import logging
from services.api_provider import api_provider as api

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("faq"))
async def faq_command(message: Message):
    """Обработчик команды /faq"""
    faq_list = await api.faq.get_faq()
    if not faq_list:
        await message.answer("Список FAQ пуст или недоступен.")
        return

    kb = InlineKeyboardBuilder()
    for faq in faq_list:
        kb.button(text=faq.question, callback_data=f"faq_{faq.id}")
    kb.button(text="◀️ Назад в меню", callback_data="main_menu")
    kb.adjust(1)

    await message.answer("📖 Выберите вопрос из списка FAQ:", reply_markup=kb.as_markup())

@router.callback_query(F.data == "faq")
async def faq_handler(callback: CallbackQuery):
    """Обработчик кнопки FAQ"""
    faq_list = await api.faq.get_faq()
    if not faq_list:
        await callback.message.edit_text("Список FAQ пуст или недоступен.")
        await callback.answer()
        return

    kb = InlineKeyboardBuilder()
    for faq in faq_list:
        kb.button(text=faq.question, callback_data=f"faq_{faq.id}")
    kb.button(text="◀️ Назад в меню", callback_data="main_menu")
    kb.adjust(1)

    await callback.message.edit_text(
        "📖 Выберите вопрос из списка FAQ:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("faq_"))
async def faq_detail_handler(callback: CallbackQuery):
    """Обработчик выбора конкретного вопроса FAQ"""
    logger.info(f"Запуск faq_detail_handler с callback_data: {callback.data}")
    
    faq_id = int(callback.data.split("_")[1])
    faq_list = await api.faq.get_faq()
    faq = next((item for item in faq_list if item.id == faq_id), None)

    if not faq:
        await callback.message.edit_text("Вопрос не найден.")
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к списку FAQ", callback_data="faq")]
    ])
    
    logger.info(f"Сформированная клавиатура: {kb}")

    await callback.message.delete()
    await callback.message.answer(
        f"❓ **Вопрос**: {faq.question}\n\n"
        f"📝 **Ответ**: {faq.answer}",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    logger.info("Сообщение отправлено")
    await callback.answer()

def register_handlers(dp):
    dp.include_router(router)
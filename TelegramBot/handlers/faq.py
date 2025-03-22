from aiogram import Router, F
from aiogram.types import (
    CallbackQuery, 
    Message, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InlineQuery, 
    InlineQueryResultArticle, 
    InputTextMessageContent
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import logging
from services.api_provider import api_provider as api
from typing import List

router = Router()
logger = logging.getLogger(__name__)

faq_cache: List["FAQ"] = []

async def load_faq_cache():
    """Загружаем FAQ из API в кэш при необходимости"""
    global faq_cache
    if not faq_cache:
        faq_list = await api.faq.get_faq()
        faq_cache = faq_list
    return faq_cache

@router.message(Command("faq"))
async def faq_command(message: Message):
    """Обработчик команды /faq"""
    faq_list = await load_faq_cache()
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
    faq_list = await load_faq_cache()
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
    faq_list = await load_faq_cache()
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

@router.inline_query()
async def inline_faq_search(inline_query: InlineQuery):
    """Обработчик inline-поиска FAQ"""
    query = inline_query.query.strip().lower()
    faq_list = await load_faq_cache()

    if not faq_list:
        await inline_query.answer(
            results=[],
            cache_time=1,
            switch_pm_text="Список FAQ пуст",
            switch_pm_parameter="faq_empty"
        )
        return

    # Фильтруем FAQ по запросу
    results = []
    for faq in faq_list:
        if query in faq.question.lower() or not query:
            results.append(
                InlineQueryResultArticle(
                    id=str(faq.id),
                    title=faq.question,
                    input_message_content=InputTextMessageContent(
                        message_text=f"❓ **Вопрос**: {faq.question}\n\n📝 **Ответ**: {faq.answer}",
                        parse_mode="Markdown"
                    ),
                    description=faq.answer[:100] + "..." if len(faq.answer) > 100 else faq.answer
                )
            )

    await inline_query.answer(
        results=results[:50],  # Telegram ограничивает до 50 результатов
        cache_time=1,
        switch_pm_text="Список FAQ",
        switch_pm_parameter="faq"
    )

def register_handlers(dp):
    dp.include_router(router)
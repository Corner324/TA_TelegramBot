from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import logging

# Импортируем клиент с другим именем для избежания конфликта
from services.api_provider import api_client as api

router = Router()
logger = logging.getLogger(__name__)

class CatalogStates(StatesGroup):
    viewing_categories = State()
    viewing_subcategories = State()
    viewing_products = State()
    viewing_product = State()


# Префиксы для callback_data
CATEGORY_PREFIX = "category_"
SUBCATEGORY_PREFIX = "subcategory_"
PRODUCT_PREFIX = "product_"
PAGE_PREFIX = "page_"
BACK_TO_CATEGORIES = "back_to_categories"
BACK_TO_SUBCATEGORIES = "back_to_subcategories"
ADD_TO_CART = "add_to_cart_"
BACK_TO_MAIN = "main_menu"


@router.callback_query(F.data == "catalog")
async def show_categories(callback: CallbackQuery, state: FSMContext):
    """Показывает список категорий"""
    # Используем импортированный API клиент с новым именем
    categories = await api.get_categories()

    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category.name, callback_data=f"{CATEGORY_PREFIX}{category.id}")

    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="◀️ Назад", callback_data=BACK_TO_MAIN)
    kb.adjust(2)

    await state.set_state(CatalogStates.viewing_categories)

    await callback.message.edit_text(
        "📋 Выберите категорию товаров:", reply_markup=kb.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith(CATEGORY_PREFIX))
async def show_subcategories(callback: CallbackQuery, state: FSMContext):
    """Показывает список подкатегорий для выбранной категории"""
    category_id = int(callback.data.split("_")[1])
    await show_subcategories_helper(callback, state, category_id)


@router.callback_query(F.data.startswith(SUBCATEGORY_PREFIX))
async def show_products(callback: CallbackQuery, state: FSMContext):
    """Показывает список товаров с пагинацией"""
    subcategory_id = int(callback.data.split("_")[1])
    await _show_products_page(callback, state, subcategory_id, 1)


@router.callback_query(F.data.startswith(PAGE_PREFIX))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает пагинацию продуктов"""
    parts = callback.data.split("_")
    subcategory_id = int(parts[1])
    page = int(parts[2])
    await _show_products_page(callback, state, subcategory_id, page)


async def _show_products_page(
    callback: CallbackQuery, state: FSMContext, subcategory_id: int, page: int
):
    """Показывает страницу с товарами"""
    products_data = await api.get_products(subcategory_id, page=page, limit=5)
    products = products_data["products"]
    total_pages = products_data["pages"]

    kb = InlineKeyboardBuilder()

    for product in products:
        kb.button(
            text=f"{product.name} - {product.price} ₽",
            callback_data=f"{PRODUCT_PREFIX}{product.id}",
        )

    # Добавляем кнопки пагинации
    pagination_row = []

    if page > 1:
        pagination_row.append(
            kb.button(text="◀️", callback_data=f"{PAGE_PREFIX}{subcategory_id}_{page-1}")
        )

    # Индикатор текущей страницы
    pagination_row.append(
        kb.button(text=f"{page}/{total_pages}", callback_data="current_page")
    )

    if page < total_pages:
        pagination_row.append(
            kb.button(text="▶️", callback_data=f"{PAGE_PREFIX}{subcategory_id}_{page+1}")
        )

    kb.button(text="◀️ Назад к подкатегориям", callback_data=BACK_TO_SUBCATEGORIES)

    # Настраиваем расположение кнопок
    kb.adjust(1)  # По одному товару в ряд

    await state.update_data(subcategory_id=subcategory_id)
    await state.set_state(CatalogStates.viewing_products)

    await callback.message.edit_text(
        f"📋 Список товаров (стр. {page} из {total_pages}):",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(PRODUCT_PREFIX))
async def show_product_details(callback: CallbackQuery, state: FSMContext):
    """Показывает детальную информацию о товаре"""
    product_id = int(callback.data.split("_")[1])
    product = await api.get_product(product_id)

    if not product:
        await callback.answer("Товар не найден")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text=f"🛒 Добавить в корзину", callback_data=f"{ADD_TO_CART}{product.id}")
    kb.button(
        text="◀️ Назад к списку товаров",
        callback_data=f"{SUBCATEGORY_PREFIX}{product.subcategory_id}",
    )
    kb.adjust(1)

    await state.update_data(product_id=product_id)
    await state.set_state(CatalogStates.viewing_product)

    # Отправляем фото товара с описанием
    await callback.message.edit_text(
        f"📦 <b>{product.name}</b>\n\n"
        f"{product.description}\n\n"
        f"💰 Цена: {product.price} ₽",
        reply_markup=kb.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == BACK_TO_CATEGORIES)
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку категорий"""
    await show_categories(callback, state)


@router.callback_query(F.data == BACK_TO_SUBCATEGORIES)
async def back_to_subcategories(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку подкатегорий"""
    data = await state.get_data()
    category_id = data.get("category_id")

    if not category_id:
        await show_categories(callback, state)
        return

    # Создаем новый callback_handler напрямую
    # Вызываем оригинальную функцию show_subcategories с category_id из состояния
    subcategory_callback = (
        callback  # Используем тот же объект, но не меняем его свойства
    )
    await show_subcategories_helper(subcategory_callback, state, category_id)


# Вспомогательная функция для отображения подкатегорий
# Код сюда перенесен из show_subcategories
async def show_subcategories_helper(
    callback: CallbackQuery, state: FSMContext, category_id: int
):
    subcategories = await api.get_subcategories(category_id)

    kb = InlineKeyboardBuilder()
    for subcategory in subcategories:
        kb.button(
            text=subcategory.name, callback_data=f"{SUBCATEGORY_PREFIX}{subcategory.id}"
        )

    kb.button(text="◀️ Назад к категориям", callback_data=BACK_TO_CATEGORIES)
    kb.adjust(2)

    await state.update_data(category_id=category_id)
    await state.set_state(CatalogStates.viewing_subcategories)

    await callback.message.edit_text(
        "📋 Выберите подкатегорию:", reply_markup=kb.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == BACK_TO_MAIN)
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)

    await callback.message.edit_text(
        f"Выберите действие в нашем магазине:",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "current_page")
async def handle_current_page(callback: CallbackQuery):
    """Обработчик нажатия на индикатор текущей страницы"""
    await callback.answer("Текущая страница", show_alert=False)


@router.callback_query(F.data.startswith(ADD_TO_CART))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Добавляет товар в корзину"""
    product_id = int(callback.data.split("_")[1])
    # Здесь будет логика добавления в корзину, которую реализуем позже
    # Пока просто показываем сообщение
    await callback.answer("Товар добавлен в корзину", show_alert=True)


def register_handlers(dp):
    dp.include_router(router)

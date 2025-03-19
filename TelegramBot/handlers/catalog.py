from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import logging
import httpx
from services.api_provider import api_provider as api
from config import API_URL

router = Router()
logger = logging.getLogger(__name__)


class CatalogStates(StatesGroup):
    viewing_categories = State()
    viewing_subcategories = State()
    viewing_products = State()
    viewing_product = State()


CATEGORY_PREFIX = "category_"
SUBCATEGORY_PREFIX = "subcategory_"
PRODUCT_PREFIX = "product_"
PAGE_PREFIX = "page_"
BACK_TO_CATEGORIES = "back_to_categories"
BACK_TO_SUBCATEGORIES = "back_to_subcategories"
ADD_TO_CART = "add_to_cart_"
BACK_TO_MAIN = "main_menu"


@router.message(Command("catalog"))
async def catalog_command(message: Message, state: FSMContext):
    """Обработчик команды /catalog"""
    categories = await api.catalog.get_categories()
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category.name, callback_data=f"{CATEGORY_PREFIX}{category.id}")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="◀️ Назад", callback_data=BACK_TO_MAIN)
    kb.adjust(2)

    await state.set_state(CatalogStates.viewing_categories)
    await message.answer("📋 Выберите категорию товаров:", reply_markup=kb.as_markup())


@router.callback_query(F.data == "catalog")
async def show_categories(callback: CallbackQuery, state: FSMContext):
    categories = await api.catalog.get_categories()
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
    category_id = int(callback.data.split("_")[1])
    await show_subcategories_helper(callback, state, category_id)


@router.callback_query(F.data.startswith(SUBCATEGORY_PREFIX))
async def show_products(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split("_")[1])
    await _show_products_page(callback, state, subcategory_id, 1)

@router.callback_query(F.data.startswith(PAGE_PREFIX))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    subcategory_id = int(parts[1])
    page = int(parts[2])
    await _show_products_page(callback, state, subcategory_id, page)

async def _show_products_page(
    callback: CallbackQuery, state: FSMContext, subcategory_id: int, page: int
):
    """Показывает страницу с товарами"""
    products_data = await api.catalog.get_products(subcategory_id, page=page, limit=5)
    products = products_data["products"]
    total_pages = products_data["pages"]

    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(
            text=f"{product.name} - {product.price} ₽",
            callback_data=f"{PRODUCT_PREFIX}{product.id}",
        )

    # Пагинация
    if page > 1:
        kb.button(text="◀️", callback_data=f"{PAGE_PREFIX}{subcategory_id}_{page-1}")
    kb.button(text=f"{page}/{total_pages}", callback_data="current_page")
    if page < total_pages:
        kb.button(text="▶️", callback_data=f"{PAGE_PREFIX}{subcategory_id}_{page+1}")

    kb.button(text="◀️ Назад к подкатегориям", callback_data=BACK_TO_SUBCATEGORIES)
    kb.adjust(1)

    await state.update_data(subcategory_id=subcategory_id)
    await state.set_state(CatalogStates.viewing_products)

    # Удаляем старое сообщение и отправляем новое
    await callback.message.delete()
    await callback.message.answer(
        f"📋 Список товаров (стр. {page} из {total_pages}):",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(PRODUCT_PREFIX))
async def show_product_details(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = await api.catalog.get_product(product_id)

    if not product:
        await callback.answer("Товар не найден")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Добавить в корзину", callback_data=f"{ADD_TO_CART}{product.id}")
    kb.button(
        text="◀️ Назад к списку товаров",
        callback_data=f"{SUBCATEGORY_PREFIX}{product.subcategory_id}",
    )
    kb.adjust(1)

    image_url = product.image_url
    logger.info(f"Загрузка изображения с URL: {image_url}")

    # Загружаем изображение с бэкенда
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content
        except httpx.HTTPError as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
            image_data = None  # Если изображение не загрузилось, показываем текст

    await state.update_data(product_id=product_id)
    await state.set_state(CatalogStates.viewing_product)

    await callback.message.delete()
    if image_data:
        # Преобразуем байты в BufferedInputFile
        photo = BufferedInputFile(file=image_data, filename="product_image.png")
        await callback.message.answer_photo(
            photo=photo,  # Передаём объект BufferedInputFile
            caption=f"📦 <b>{product.name}</b>\n\n"
            f"{product.description}\n\n"
            f"💰 Цена: {product.price} ₽",
            reply_markup=kb.as_markup(),
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            text=f"📦 <b>{product.name}</b>\n\n"
            f"{product.description}\n\n"
            f"💰 Цена: {product.price} ₽\n\n(Изображение недоступно)",
            reply_markup=kb.as_markup(),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data == BACK_TO_CATEGORIES)
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await show_categories(callback, state)


@router.callback_query(F.data == BACK_TO_SUBCATEGORIES)
async def back_to_subcategories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data.get("category_id")
    if not category_id:
        await show_categories(callback, state)
        return
    await show_subcategories_helper(callback, state, category_id)


async def show_subcategories_helper(
    callback: CallbackQuery, state: FSMContext, category_id: int
):
    subcategories = await api.catalog.get_subcategories(category_id)
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
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)
    await callback.message.edit_text(
        "Выберите действие в нашем магазине:",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "current_page")
async def handle_current_page(callback: CallbackQuery):
    await callback.answer("Текущая страница", show_alert=False)


@router.callback_query(F.data.startswith(ADD_TO_CART))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await callback.answer("Товар добавлен в корзину", show_alert=True)


def register_handlers(dp):
    dp.include_router(router)

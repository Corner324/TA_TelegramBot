import uuid
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import logging
import httpx
from services.api_provider import api_provider as api
from services.cart_service import CartService  # Импортируем CartService напрямую
from config import REDIS_DSN

router = Router()
logger = logging.getLogger(__name__)

# Инициализация сервиса корзины
cart_service = CartService(REDIS_DSN)

class CatalogStates(StatesGroup):
    """Состояния FSM для управления каталогом."""
    viewing_categories = State()
    viewing_subcategories = State()
    viewing_products = State()
    viewing_product = State()
    selecting_quantity = State()

# Константы
CATEGORY_PREFIX = "category_"
SUBCATEGORY_PREFIX = "subcategory_"
PRODUCT_PREFIX = "product_"
PAGE_PREFIX = "page_"
BACK_TO_CATEGORIES = "back_to_categories"
BACK_TO_SUBCATEGORIES = "back_to_subcategories"
ADD_TO_CART = "add_to_cart_"
QUANTITY_PREFIX = "quantity_"
CONFIRM_ADD = "confirm_add_"
BACK_TO_MAIN = "main_menu"

@router.message(Command("catalog"))
async def catalog_command(message: Message, state: FSMContext) -> None:
    """Обработчик команды /catalog для отображения категорий.

    Args:
        message: Входящее сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
    """
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
async def show_categories(callback: CallbackQuery, state: FSMContext) -> None:
    """Отображение списка категорий по callback-запросу.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
    """
    categories = await api.catalog.get_categories()
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category.name, callback_data=f"{CATEGORY_PREFIX}{category.id}")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="◀️ Назад", callback_data=BACK_TO_MAIN)
    kb.adjust(2)
    await state.set_state(CatalogStates.viewing_categories)
    await callback.message.edit_text("📋 Выберите категорию товаров:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith(CATEGORY_PREFIX))
async def show_subcategories(callback: CallbackQuery, state: FSMContext) -> None:
    """Отображение подкатегорий выбранной категории.

    Args:
        callback: Callback-запрос от кнопки категории.
        state: Контекст FSM для управления состояниями.
    """
    category_id = int(callback.data.split("_")[1])
    await show_subcategories_helper(callback, state, category_id)

@router.callback_query(F.data.startswith(SUBCATEGORY_PREFIX))
async def show_products(callback: CallbackQuery, state: FSMContext) -> None:
    """Отображение продуктов выбранной подкатегории.

    Args:
        callback: Callback-запрос от кнопки подкатегории.
        state: Контекст FSM для управления состояниями.
    """
    subcategory_id = int(callback.data.split("_")[1])
    await _show_products_page(callback, state, subcategory_id, 1)

@router.callback_query(F.data.startswith(PAGE_PREFIX))
async def handle_pagination(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка пагинации списка продуктов.

    Args:
        callback: Callback-запрос от кнопок пагинации.
        state: Контекст FSM для управления состояниями.
    """
    parts = callback.data.split("_")
    subcategory_id = int(parts[1])
    page = int(parts[2])
    await _show_products_page(callback, state, subcategory_id, page)

async def _show_products_page(callback: CallbackQuery, state: FSMContext, subcategory_id: int, page: int) -> None:
    """Внутренняя функция для отображения страницы продуктов.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
        subcategory_id: ID подкатегории.
        page: Номер страницы.
    """
    products_data = await api.catalog.get_products(subcategory_id, page=page, limit=5)
    products = products_data["products"]
    total_pages = products_data["pages"]
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(text=f"{product.name} - {product.price} ₽", callback_data=f"{PRODUCT_PREFIX}{product.id}")
    if page > 1:
        kb.button(text="◀️", callback_data=f"{PAGE_PREFIX}{subcategory_id}_{page-1}")
    kb.button(text=f"{page}/{total_pages}", callback_data="current_page")
    if page < total_pages:
        kb.button(text="▶️", callback_data=f"{PAGE_PREFIX}{subcategory_id}_{page+1}")
    kb.button(text="◀️ Назад к подкатегориям", callback_data=BACK_TO_SUBCATEGORIES)
    kb.adjust(1)
    await state.update_data(subcategory_id=subcategory_id)
    await state.set_state(CatalogStates.viewing_products)
    await callback.message.delete()
    await callback.message.answer(f"📋 Список товаров (стр. {page} из {total_pages}):", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith(ADD_TO_CART))
async def select_quantity(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбор количества товара для добавления в корзину.

    Args:
        callback: Callback-запрос от кнопки "Добавить в корзину".
        state: Контекст FSM для управления состояниями.
    """
    parts = callback.data.split("_")
    try:
        product_id = int(parts[-1])
    except (IndexError, ValueError) as e:
        logger.error(f"Некорректный callback.data: {callback.data}, ошибка: {e}")
        await callback.answer("Произошла ошибка при выборе товара", show_alert=True)
        return
    await state.update_data(product_id=product_id)
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.button(text=str(i), callback_data=f"{QUANTITY_PREFIX}{product_id}_{i}")
    kb.button(text="◀️ Назад", callback_data=f"{PRODUCT_PREFIX}{product_id}")
    kb.adjust(2)
    await state.set_state(CatalogStates.selecting_quantity)
    await callback.message.edit_caption(caption="Выберите количество:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith(QUANTITY_PREFIX))
async def confirm_quantity(callback: CallbackQuery, state: FSMContext) -> None:
    """Подтверждение выбранного количества товара.

    Args:
        callback: Callback-запрос от кнопки количества.
        state: Контекст FSM для управления состояниями.
    """
    parts = callback.data.split("_")
    try:
        product_id = int(parts[1])
        quantity = int(parts[2])
    except (IndexError, ValueError) as e:
        logger.error(f"Некорректный callback.data: {callback.data}, ошибка: {e}")
        await callback.answer("Произошла ошибка при выборе количества", show_alert=True)
        return
    await state.update_data(quantity=quantity)
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"{CONFIRM_ADD}{product_id}")
    kb.button(text="◀️ Назад", callback_data=f"{PRODUCT_PREFIX}{product_id}")
    kb.adjust(1)
    await callback.message.edit_caption(
        caption=f"Добавить {quantity} шт. в корзину?",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith(CONFIRM_ADD))
async def add_to_cart(callback: CallbackQuery, state: FSMContext) -> None:
    """Добавление товара в корзину после подтверждения.

    Args:
        callback: Callback-запрос от кнопки подтверждения.
        state: Контекст FSM для управления состояниями.
    """
    parts = callback.data.split("_")
    try:
        product_id = int(parts[-1])
    except (IndexError, ValueError) as e:
        logger.error(f"Некорректный callback.data: {callback.data}, ошибка: {e}")
        await callback.answer("Произошла ошибка при добавлении в корзину", show_alert=True)
        return
    data = await state.get_data()
    quantity = data["quantity"]
    user_id = callback.from_user.id
    product = await api.catalog.get_product(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    cart = await cart_service.get_cart(user_id)  # Используем cart_service
    cart.add_item(product, quantity)
    await cart_service.save_cart(user_id, cart)  # Используем cart_service
    await callback.answer("Товар добавлен в корзину!", show_alert=True)
    await state.update_data(product_id=product_id)
    await show_product_details(callback, state)

@router.callback_query(F.data.startswith(PRODUCT_PREFIX))
async def show_product_details(callback: CallbackQuery, state: FSMContext) -> None:
    """Отображение деталей товара.

    Args:
        callback: Callback-запрос от кнопки продукта.
        state: Контекст FSM для управления состояниями.
    """
    parts = callback.data.split("_")
    try:
        product_id = int(parts[1])
    except (IndexError, ValueError):
        data = await state.get_data()
        product_id = data.get("product_id")
        if not product_id:
            logger.error(f"Некорректный callback.data и нет product_id в state: {callback.data}")
            await callback.answer("Произошла ошибка при отображении товара", show_alert=True)
            return
    product = await api.catalog.get_product(product_id)
    if not product:
        await callback.answer("Товар не найден")
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Добавить в корзину", callback_data=f"{ADD_TO_CART}{product.id}")
    kb.button(text="◀️ Назад к списку товаров", callback_data=f"{SUBCATEGORY_PREFIX}{product.subcategory_id}")
    kb.adjust(1)
    image_url = product.image_url
    logger.info(f"Загрузка изображения с URL: {image_url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content
        except httpx.HTTPError as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
            image_data = None
    await state.update_data(product_id=product_id)
    await state.set_state(CatalogStates.viewing_product)
    await callback.message.delete()
    if image_data:
        photo = BufferedInputFile(file=image_data, filename="product_image.png")
        await callback.message.answer_photo(
            photo=photo,
            caption=f"📦 <b>{product.name}</b>\n\n{product.description}\n\n💰 Цена: {product.price} ₽",
            reply_markup=kb.as_markup(),
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            text=f"📦 <b>{product.name}</b>\n\n{product.description}\n\n💰 Цена: {product.price} ₽\n\n(Изображение недоступно)",
            reply_markup=kb.as_markup(),
            parse_mode="HTML",
        )
    await callback.answer()

@router.callback_query(F.data == BACK_TO_CATEGORIES)
async def back_to_categories(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат к списку категорий.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
    """
    await show_categories(callback, state)

@router.callback_query(F.data == BACK_TO_SUBCATEGORIES)
async def back_to_subcategories(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат к списку подкатегорий.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
    """
    data = await state.get_data()
    category_id = data.get("category_id")
    if not category_id:
        await show_categories(callback, state)
        return
    await show_subcategories_helper(callback, state, category_id)

async def show_subcategories_helper(callback: CallbackQuery, state: FSMContext, category_id: int) -> None:
    """Внутренняя функция для отображения подкатегорий.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
        category_id: ID категории.
    """
    subcategories = await api.catalog.get_subcategories(category_id)
    kb = InlineKeyboardBuilder()
    for subcategory in subcategories:
        kb.button(text=subcategory.name, callback_data=f"{SUBCATEGORY_PREFIX}{subcategory.id}")
    kb.button(text="◀️ Назад к категориям", callback_data=BACK_TO_CATEGORIES)
    kb.adjust(2)
    await state.update_data(category_id=category_id)
    await state.set_state(CatalogStates.viewing_subcategories)
    await callback.message.edit_text("📋 Выберите подкатегорию:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data == BACK_TO_MAIN)
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в главное меню.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="❓ FAQ", callback_data="faq")
    kb.adjust(2)
    await callback.message.edit_text("Выберите действие в нашем магазине:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data == "current_page")
async def handle_current_page(callback: CallbackQuery) -> None:
    """Обработка нажатия на текущую страницу (информационное действие).

    Args:
        callback: Callback-запрос от кнопки текущей страницы.
    """
    await callback.answer("Текущая страница", show_alert=False)

def register_handlers(dp) -> None:
    """Регистрация обработчиков в диспетчере.

    Args:
        dp: Диспетчер aiogram для регистрации роутера.
    """
    dp.include_router(router)
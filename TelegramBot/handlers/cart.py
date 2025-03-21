import uuid
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
import logging
from typing import Dict, Any
from services.cart_service import CartService
from services.payment_service import PaymentService
from repositories.order_repository import OrderExcelRepository
from config import REDIS_DSN

router = Router()
logger = logging.getLogger(__name__)

# Константы
CART_PREFIX = "cart"
REMOVE_FROM_CART_PREFIX = "remove_from_cart_"
CHECKOUT_CALLBACK = "checkout"
EMPTY_CART_MESSAGE = "🛒 Ваша корзина пуста"
BACK_TO_CATALOG_TEXT = "◀️ Назад к каталогу"
CATALOG_CALLBACK = "catalog"


class CartStates(StatesGroup):
    """Состояния FSM для управления процессом оформления заказа."""
    viewing_cart = State()
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_phone = State()


# Инициализация зависимостей
cart_service = CartService(REDIS_DSN)
payment_service = PaymentService()
order_repository = OrderExcelRepository("orders.xlsx")


@router.message(Command("cart"))
async def cart_command(message: Message, state: FSMContext) -> None:
    """Обработчик команды /cart для отображения корзины пользователя.

    Args:
        message: Входящее сообщение от пользователя.
        state: Контекст FSM для управления состояниями.
    """
    await _show_cart(message, state, message.from_user.id)


@router.callback_query(F.data == CART_PREFIX)
async def show_cart_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик callback-запроса для отображения корзины.

    Args:
        callback: Callback-запрос от кнопки.
        state: Контекст FSM для управления состояниями.
    """
    await _show_cart(callback.message, state, callback.from_user.id)
    await callback.answer()


async def _show_cart(message: Message, state: FSMContext, user_id: int) -> None:
    """Внутренняя функция для отображения содержимого корзины.

    Args:
        message: Сообщение для ответа пользователю.
        state: Контекст FSM для управления состояниями.
        user_id: Идентификатор пользователя.
    """
    cart = await cart_service.get_cart(user_id)
    if cart.is_empty():
        kb = InlineKeyboardBuilder()
        kb.button(text="📋 Каталог", callback_data=CATALOG_CALLBACK)
        kb.adjust(1)
        await message.answer(EMPTY_CART_MESSAGE, reply_markup=kb.as_markup())
        return

    response = "🛒 Ваша корзина:\n"
    kb = InlineKeyboardBuilder()
    for item in cart.items:
        response += (
            f"{item.product.name} x{item.quantity} - "
            f"{item.product.price * item.quantity:.2f} ₽\n"
        )
        kb.button(
            text=f"Удалить {item.product.name}",
            callback_data=f"{REMOVE_FROM_CART_PREFIX}{item.product.id}",
        )
    response += f"Итого: {cart.get_total():.2f} ₽"
    kb.button(text="Оформить заказ", callback_data=CHECKOUT_CALLBACK)
    kb.button(text=BACK_TO_CATALOG_TEXT, callback_data=CATALOG_CALLBACK)
    kb.adjust(1)
    await state.set_state(CartStates.viewing_cart)
    await message.answer(response, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith(REMOVE_FROM_CART_PREFIX))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext) -> None:
    """Удаление товара из корзины по callback-запросу.

    Args:
        callback: Callback-запрос от кнопки удаления.
        state: Контекст FSM для управления состояниями.
    """
    parts = callback.data.split("_")
    try:
        product_id = int(parts[-1])
    except (IndexError, ValueError) as e:
        logger.error(f"Invalid callback data: {callback.data}, error: {e}")
        await callback.answer("Ошибка при удалении товара", show_alert=True)
        return

    user_id = callback.from_user.id
    cart = await cart_service.get_cart(user_id)
    cart.remove_item(product_id)
    await cart_service.save_cart(user_id, cart)
    await callback.answer("Товар удалён из корзины")
    await _show_cart(callback.message, state, user_id)


@router.callback_query(F.data == CHECKOUT_CALLBACK)
async def start_checkout(callback: CallbackQuery, state: FSMContext) -> None:
    """Начало процесса оформления заказа.

    Args:
        callback: Callback-запрос от кнопки "Оформить заказ".
        state: Контекст FSM для управления состояниями.
    """
    user_id = callback.from_user.id
    cart = await cart_service.get_cart(user_id)
    if cart.is_empty():
        await callback.message.edit_text(
            EMPTY_CART_MESSAGE, reply_markup=_back_to_catalog_kb()
        )
        return
    await state.set_state(CartStates.waiting_for_name)
    await callback.message.edit_text("Введите ваше имя:")


@router.message(StateFilter(CartStates.waiting_for_name), F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    """Обработка ввода имени пользователя в процессе оформления.

    Args:
        message: Входящее сообщение с именем.
        state: Контекст FSM для управления состояниями.
    """
    await state.update_data(name=message.text)
    await state.set_state(CartStates.waiting_for_address)
    await message.answer("Введите ваш адрес:")


@router.message(StateFilter(CartStates.waiting_for_address), F.text)
async def process_address(message: Message, state: FSMContext) -> None:
    """Обработка ввода адреса пользователя в процессе оформления.

    Args:
        message: Входящее сообщение с адресом.
        state: Контекст FSM для управления состояниями.
    """
    await state.update_data(address=message.text)
    await state.set_state(CartStates.waiting_for_phone)
    await message.answer("Введите ваш телефон:")


@router.message(StateFilter(CartStates.waiting_for_phone), F.text)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Обработка ввода телефона и завершение оформления заказа.

    Args:
        message: Входящее сообщение с телефоном.
        state: Контекст FSM для управления состояниями.
    """
    user_id = message.from_user.id
    data = await state.get_data()
    cart = await cart_service.get_cart(user_id)
    total = cart.get_total()
    order = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "items": cart.items[:],
        "total": total,
        "name": data["name"],
        "address": data["address"],
        "phone": message.text,
        "status": "pending",
    }
    payment = await payment_service.create_payment(total, order["id"])
    order_repository.save_order(order)
    kb = InlineKeyboardBuilder()
    # kb.button(text="Оплатить", url=payment["confirmation"]["confirmation_url"])
    kb.button(text="Оплатить", callback_data=CATALOG_CALLBACK)
    kb.button(text=BACK_TO_CATALOG_TEXT, callback_data=CATALOG_CALLBACK)
    await message.answer(
        f"Заказ сформирован! Сумма: {total:.3f} ₽\nДля оплаты перейдите по ссылке:",
        reply_markup=kb.as_markup(),
    )
    await cart_service.clear_cart(user_id)
    # await state.finish()


def _back_to_catalog_kb() -> InlineKeyboardBuilder:
    """Создание клавиатуры для возврата в каталог.

    Returns:
        InlineKeyboardBuilder: Клавиатура с кнопкой возврата в каталог.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Каталог", callback_data=CATALOG_CALLBACK)
    return kb.as_markup()


def register_handlers(dp) -> None:
    """Регистрация обработчиков в диспетчере.

    Args:
        dp: Диспетчер aiogram для регистрации роутера.
    """
    dp.include_router(router)
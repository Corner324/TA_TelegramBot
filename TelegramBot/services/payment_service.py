from typing import Dict, Any
import stripe
import logging
from config import STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


class PaymentService:
    """Сервис для работы с платежами через Stripe."""

    MIN_AMOUNT_RUB = 50.00

    def __init__(self) -> None:
        """Инициализация сервиса оплаты."""
        stripe.api_key = STRIPE_SECRET_KEY

    async def create_payment(self, amount: float, order_id: str) -> Dict[str, Any]:
        """Создание платежной сессии через Stripe."""
        if amount < self.MIN_AMOUNT_RUB:
            logger.warning(
                f"Сумма {amount} ₽ меньше минимальной ({self.MIN_AMOUNT_RUB} ₽)"
            )
            return {
                "error": f"Сумма заказа должна быть не менее {self.MIN_AMOUNT_RUB} ₽"
            }

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "rub",
                            "product_data": {"name": "Заказ из Telegram-бота"},
                            "unit_amount": int(amount * 100),  # Сумма в копейках
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="https://t.me/Market3245bot?start=success_{}".format(
                    order_id
                ),
                cancel_url="https://t.me/Market3245bot?start=cancel_{}".format(
                    order_id
                ),
                metadata={"order_id": order_id},
            )
            return {"confirmation_url": session.url}
        except stripe.error.StripeError as e:
            logger.error(f"Ошибка при создании платежной сессии: {e}")
            return {"error": str(e)}

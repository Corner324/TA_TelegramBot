from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """Сервис для работы с платежами."""

    def __init__(self) -> None:
        """Инициализация сервиса оплаты."""
        self._payment_url = "https://api.yookassa.ru/v3/payments"
        self._auth = ("test_shop_id", "test_secret_key")

    async def create_payment(self, amount: float, order_id: str) -> Dict[str, Any]:
        """Создание тестового платежа через YooKassa."""

        ...
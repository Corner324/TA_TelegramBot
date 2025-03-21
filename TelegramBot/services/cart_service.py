import json
from redis.asyncio import Redis
from models.cart import Cart
from typing import List


class CartService:
    """Сервис для управления корзиной пользователя."""

    def __init__(self, redis_dsn: str) -> None:
        """Инициализация сервиса с подключением к Redis.

        Args:
            redis_dsn: Строка подключения к Redis.
        """
        self._redis_client = Redis.from_url(redis_dsn, decode_responses=True)

    async def get_cart(self, user_id: int) -> Cart:
        """Получение корзины пользователя из Redis.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Cart: Объект корзины пользователя.
        """
        cart_data = await self._redis_client.get(f"cart:{user_id}")
        if cart_data:
            return Cart.from_dict(json.loads(cart_data))
        return Cart(items=[])

    async def save_cart(self, user_id: int, cart: Cart) -> None:
        """Сохранение корзины пользователя в Redis.

        Args:
            user_id: Идентификатор пользователя.
            cart: Объект корзины для сохранения.
        """
        await self._redis_client.set(f"cart:{user_id}", json.dumps(cart.to_dict()))

    async def clear_cart(self, user_id: int) -> None:
        """Очистка корзины пользователя в Redis.

        Args:
            user_id: Идентификатор пользователя.
        """
        await self._redis_client.delete(f"cart:{user_id}")
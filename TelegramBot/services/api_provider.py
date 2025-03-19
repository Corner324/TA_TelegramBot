import os
import logging
from services.fake_data import FakeApiClient
from services.api_client import ApiClient

logger = logging.getLogger(__name__)

# Переключение между реальным и фейковым API
USE_FAKE_API = os.getenv("USE_FAKE_API", "True").lower() == "true"


def get_api_client():
    """Возвращает экземпляр API клиента (фейковый или реальный)"""
    try:
        if USE_FAKE_API:
            logger.info("Используем фейковый API клиент")
            return FakeApiClient()
        else:
            logger.info("Используем реальный API клиент")
            return ApiClient()
    except Exception as e:
        logger.error(f"Ошибка при инициализации API клиента: {e}")
        logger.info("Переключаемся на фейковый API клиент")
        return FakeApiClient()


# Создаем единственный экземпляр клиента для использования во всем приложении
api_client = get_api_client()

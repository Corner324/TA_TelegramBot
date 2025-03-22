import httpx
import logging
from typing import Dict, Any, Optional
from config import API_URL

logger = logging.getLogger(__name__)


class BackendUnavailableError(Exception):
    """Исключение для случаев, когда бэкенд недоступен"""

    pass


class HttpClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.headers = {}

    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        kwargs["headers"] = {**self.headers, **kwargs.get("headers", {})}

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Отправка {method} запроса на {url}")
                response = await getattr(client, method.lower())(url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Ошибка HTTP: {e} - Ответ: {e.response.text}")
                raise
            except (httpx.RequestError, OSError) as e:
                logger.error(f"Сетевая ошибка при запросе {url}: {e}")
                raise BackendUnavailableError("Бэкенд временно недоступен")
            except Exception as e:
                logger.error(f"Неизвестная ошибка при запросе {url}: {e}")
                raise

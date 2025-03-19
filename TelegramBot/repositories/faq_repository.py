from typing import List
import logging
from infrastructure.http_client import HttpClient
from models.faq import FAQ

logger = logging.getLogger(__name__)

class FAQRepository:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def get_faq(self) -> List[FAQ]:
        try:
            data = await self.http_client.request("get", "/api/faq/")
            if not data or "results" not in data:
                logger.warning("Нет данных FAQ или отсутствует ключ 'results'")
                return []
            return [FAQ.from_dict(item) for item in data["results"]]
        except Exception as e:
            logger.error(f"Ошибка при получении FAQ: {e}")
            return []
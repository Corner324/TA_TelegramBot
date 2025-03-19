import httpx
import logging
from typing import List, Optional, Dict, Any
from config import API_URL
from models.catalog import Category, Subcategory, Product

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})
        headers["Host"] = "backend_api.local"
        kwargs["headers"] = headers
        async with httpx.AsyncClient() as client:
            try:
                response = await getattr(client, method.lower())(url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Ошибка HTTP: {e} - Ответ: {e.response.text}")
                return {"error": str(e)}
            except Exception as e:
                logger.error(f"Ошибка при запросе {url}: {e}")
                return {"error": str(e)}

    async def get_categories(self) -> List[Category]:
        """Получает список категорий из API"""
        data = await self._make_request("get", "/api/categories/")
        if "error" in data or not data.get("results"):
            return []
        return [Category.from_dict(item) for item in data.get("results", [])]

    async def get_subcategories(self, category_id: int) -> List[Subcategory]:
        """Получает список подкатегорий для указанной категории"""
        data = await self._make_request(
            "get", f"/api/categories/{category_id}/subcategories/"
        )
        if "error" in data:
            return []
        return [Subcategory.from_dict(item) for item in data]

    async def get_products(self, subcategory_id: int, page: int = 1, limit: int = 5) -> Dict[str, Any]:
        """Получает список товаров с пагинацией"""
        data = await self._make_request(
            "get",
            f"/api/subcategories/{subcategory_id}/products/",
            params={"page": page, "limit": limit},
        )
        logger.info(f"Ответ от бэкенда для продуктов: {data}")

        if "error" in data:
            logger.warning(f"Ошибка в данных: {data['error']}")
            return {"products": [], "total": 0, "pages": 0}

        # Извлекаем вложенные данные
        results = data.get("results", {})
        product_list = results.get("items", [])
        products = [Product.from_dict(item) for item in product_list]
        
        return {
            "products": products,
            "total": results.get("total", data.get("count", 0)),
            "pages": results.get("pages", 0),
        }

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Получает детальную информацию о товаре"""
        data = await self._make_request("get", f"/api/products/{product_id}/")
        if "error" in data:
            return None
        return Product.from_dict(data)

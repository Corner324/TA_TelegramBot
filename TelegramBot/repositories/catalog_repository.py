from typing import List, Dict, Any, Optional
import logging
from infrastructure.http_client import HttpClient
from models.catalog import Category, Subcategory, Product

logger = logging.getLogger(__name__)

class CatalogRepository:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def get_categories(self) -> List[Category]:
        try:
            data = await self.http_client.request("get", "/api/categories/")
            if not data.get("results"):
                logger.warning("Нет данных о категориях")
                return []
            return [Category.from_dict(item) for item in data.get("results", [])]
        except Exception as e:
            logger.error(f"Ошибка при получении категорий: {e}")
            return []

    async def get_subcategories(self, category_id: int) -> List[Subcategory]:
        try:
            data = await self.http_client.request("get", f"/api/categories/{category_id}/subcategories/")
            if not data:
                logger.warning(f"Нет подкатегорий для категории {category_id}")
                return []
            return [Subcategory.from_dict(item) for item in data]
        except Exception as e:
            logger.error(f"Ошибка при получении подкатегорий: {e}")
            return []

    async def get_products(self, subcategory_id: int, page: int = 1, limit: int = 5) -> Dict[str, Any]:
        try:
            data = await self.http_client.request(
                "get",
                f"/api/subcategories/{subcategory_id}/products/",
                params={"page": page, "limit": limit},
            )
            results = data.get("results", {})
            product_list = results.get("items", [])
            products = [Product.from_dict(item) for item in product_list]
            return {
                "products": products,
                "total": results.get("total", data.get("count", 0)),
                "pages": results.get("pages", 0),
            }
        except Exception as e:
            logger.error(f"Ошибка при получении товаров: {e}")
            return {"products": [], "total": 0, "pages": 0}

    async def get_product(self, product_id: int) -> Optional[Product]:
        try:
            data = await self.http_client.request("get", f"/api/products/{product_id}/")
            return Product.from_dict(data) if data else None
        except Exception as e:
            logger.error(f"Ошибка при получении товара {product_id}: {e}")
            return None
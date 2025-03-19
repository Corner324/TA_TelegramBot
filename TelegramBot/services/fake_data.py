from typing import List, Dict, Any, Optional
from models.catalog import Category, Subcategory, Product
import logging

logger = logging.getLogger(__name__)

# Фейковые данные для разработки, пока API не готово
FAKE_CATEGORIES = [
    {"id": 1, "name": "Одежда", "image_url": "https://example.com/clothes.jpg"},
    {
        "id": 2,
        "name": "Электроника",
        "image_url": "https://example.com/electronics.jpg",
    },
    {"id": 3, "name": "Книги", "image_url": "https://example.com/books.jpg"},
]

FAKE_SUBCATEGORIES = {
    1: [  # Одежда
        {
            "id": 1,
            "category_id": 1,
            "name": "Футболки",
            "image_url": "https://example.com/tshirts.jpg",
        },
        {
            "id": 2,
            "category_id": 1,
            "name": "Джинсы",
            "image_url": "https://example.com/jeans.jpg",
        },
    ],
    2: [  # Электроника
        {
            "id": 3,
            "category_id": 2,
            "name": "Смартфоны",
            "image_url": "https://example.com/smartphones.jpg",
        },
        {
            "id": 4,
            "category_id": 2,
            "name": "Ноутбуки",
            "image_url": "https://example.com/laptops.jpg",
        },
    ],
    3: [  # Книги
        {
            "id": 5,
            "category_id": 3,
            "name": "Художественная литература",
            "image_url": "https://example.com/fiction.jpg",
        },
        {
            "id": 6,
            "category_id": 3,
            "name": "Научная литература",
            "image_url": "https://example.com/science.jpg",
        },
    ],
}

FAKE_PRODUCTS = {
    1: [  # Футболки
        {
            "id": 1,
            "subcategory_id": 1,
            "name": "Футболка белая",
            "description": "Классическая белая футболка",
            "price": 1500,
            "image_url": "https://example.com/white_tshirt.jpg",
        },
        {
            "id": 2,
            "subcategory_id": 1,
            "name": "Футболка черная",
            "description": "Классическая черная футболка",
            "price": 1500,
            "image_url": "https://example.com/black_tshirt.jpg",
        },
        {
            "id": 3,
            "subcategory_id": 1,
            "name": "Футболка красная",
            "description": "Классическая красная футболка",
            "price": 1600,
            "image_url": "https://example.com/red_tshirt.jpg",
        },
    ],
    2: [  # Джинсы
        {
            "id": 4,
            "subcategory_id": 2,
            "name": "Джинсы синие",
            "description": "Классические синие джинсы",
            "price": 3500,
            "image_url": "https://example.com/blue_jeans.jpg",
        },
        {
            "id": 5,
            "subcategory_id": 2,
            "name": "Джинсы черные",
            "description": "Классические черные джинсы",
            "price": 3500,
            "image_url": "https://example.com/black_jeans.jpg",
        },
    ],
    3: [  # Смартфоны
        {
            "id": 6,
            "subcategory_id": 3,
            "name": "Смартфон X",
            "description": "Мощный смартфон",
            "price": 50000,
            "image_url": "https://example.com/smartphone_x.jpg",
        },
        {
            "id": 7,
            "subcategory_id": 3,
            "name": "Смартфон Y",
            "description": "Недорогой смартфон",
            "price": 15000,
            "image_url": "https://example.com/smartphone_y.jpg",
        },
    ],
}


class FakeApiClient:
    """Эмуляция API клиента с фейковыми данными"""

    async def get_categories(self) -> List[Category]:
        return [Category.from_dict(item) for item in FAKE_CATEGORIES]

    async def get_subcategories(self, category_id: int) -> List[Subcategory]:
        subcategories = FAKE_SUBCATEGORIES.get(category_id, [])
        return [Subcategory.from_dict(item) for item in subcategories]

    async def get_products(
        self, subcategory_id: int, page: int = 1, limit: int = 2
    ) -> Dict[str, Any]:
        all_products = FAKE_PRODUCTS.get(subcategory_id, [])

        # Реализация пагинации
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_products = all_products[start_idx:end_idx]

        total_products = len(all_products)
        total_pages = (total_products + limit - 1) // limit

        products = [Product.from_dict(item) for item in page_products]
        return {"products": products, "total": total_products, "pages": total_pages}

    async def get_product(self, product_id: int) -> Optional[Product]:
        # Находим товар по ID
        for subcategory_products in FAKE_PRODUCTS.values():
            for product in subcategory_products:
                if product["id"] == product_id:
                    return Product.from_dict(product)
        return None

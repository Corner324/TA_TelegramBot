from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Category:
    id: int
    name: str
    image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(id=data["id"], name=data["name"], image_url=data.get("image_url"))


@dataclass
class Subcategory:
    id: int
    category_id: int
    name: str
    image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            category_id=data["category_id"],
            name=data["name"],
            image_url=data.get("image_url"),
        )


@dataclass
class Product:
    id: int
    subcategory_id: int
    name: str
    description: str
    price: float
    image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            subcategory_id=data["subcategory_id"],
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image_url=data.get("image_url"),
        )

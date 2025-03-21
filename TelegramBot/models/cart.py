from dataclasses import dataclass
from typing import List, Optional

from models.catalog import Product

@dataclass
class CartItem:
    product: Product
    quantity: int

    @classmethod
    def from_dict(cls, data: dict):
        product = Product.from_dict(data["product"])
        return cls(product=product, quantity=data["quantity"])

    def to_dict(self):
        return {"product": vars(self.product), "quantity": self.quantity}

@dataclass
class Cart:
    items: List[CartItem]

    @classmethod
    def from_dict(cls, data: dict):
        items = [CartItem.from_dict(item) for item in data.get("items", [])]
        return cls(items=items)

    def to_dict(self):
        return {"items": [item.to_dict() for item in self.items]}

    def add_item(self, product: Product, quantity: int):
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product=product, quantity=quantity))

    def remove_item(self, product_id: int):
        self.items = [item for item in self.items if item.product.id != product_id]

    def get_total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0
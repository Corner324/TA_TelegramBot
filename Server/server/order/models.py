from django.db import models

from catalog.models import Product

class Order(models.Model):
    user_id = models.BigIntegerField(verbose_name="ID пользователя в Telegram")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итого")
    name = models.CharField(max_length=255, verbose_name="Имя")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    status = models.CharField(max_length=20, default="pending", verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.id} от {self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент заказа")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
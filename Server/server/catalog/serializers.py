from rest_framework import serializers
from .models import Category, Subcategory, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep["image_url"] = instance.image.url
        return rep


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ["id", "category", "name", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category.id
        if instance.image:
            rep["image_url"] = instance.image.url
        return rep


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "subcategory", "name", "description", "price", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subcategory_id"] = instance.subcategory.id
        if instance.image:
            rep["image_url"] = instance.image.url
        return rep

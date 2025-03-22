from rest_framework import serializers
from .models import Category, Subcategory, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "subcategory", "name", "description", "price", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subcategory_id"] = instance.subcategory.id
        request = self.context.get("request")
        if instance.image and instance.image.url:
            if request:
                rep["image_url"] = request.build_absolute_uri(instance.image.url)
            else:
                rep["image_url"] = f"http://backend_api:8000{instance.image.url}"
        else:
            if request:
                rep["image_url"] = request.build_absolute_uri(
                    "/static/images/default_product_image.jpg"
                )
            else:
                rep["image_url"] = (
                    "http://backend_api:8000/static/images/default_product_image.jpg"
                )
        return rep


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ["id", "category", "name", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category.id
        request = self.context.get("request")
        if instance.image and instance.image.url:
            if request:
                rep["image_url"] = request.build_absolute_uri(instance.image.url)
            else:
                rep["image_url"] = f"http://backend_api:8000{instance.image.url}"
        return rep


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        if instance.image and instance.image.url:
            if request:
                rep["image_url"] = request.build_absolute_uri(instance.image.url)
            else:
                rep["image_url"] = f"http://backend_api:8000{instance.image.url}"
        return rep

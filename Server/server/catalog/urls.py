from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, SubcategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("subcategories", SubcategoryViewSet, basename="subcategories")
router.register("products", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
]

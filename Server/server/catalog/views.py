from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Category, Subcategory, Product
from .serializers import CategorySerializer, SubcategorySerializer, ProductSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "limit"
    max_page_size = 20

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"])
    def subcategories(self, request, pk=None):
        category = self.get_object()
        subcategories = category.subcategories.all()
        serializer = SubcategorySerializer(subcategories, many=True, context={"request": request})
        return Response(serializer.data)

class SubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        subcategory = self.get_object()
        queryset = subcategory.products.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(
                {
                    "items": serializer.data,
                    "total": queryset.count(),
                    "pages": (queryset.count() + self.paginator.page_size - 1) // self.paginator.page_size,
                }
            )

        serializer = ProductSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
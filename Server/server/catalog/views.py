from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from asgiref.sync import sync_to_async, async_to_sync
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
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["get"])
    def subcategories(self, request, pk=None):
        @async_to_sync
        async def get_subcategories():
            category = await sync_to_async(self.get_object)()
            subcategories = await sync_to_async(list)(category.subcategories.all())
            return subcategories

        subcategories = get_subcategories()
        serializer = SubcategorySerializer(
            subcategories, many=True, context={"request": request}
        )
        return Response(serializer.data)


class SubcategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        @async_to_sync
        async def get_products():
            subcategory = await sync_to_async(self.get_object)()
            queryset = await sync_to_async(list)(subcategory.products.all())
            return queryset

        queryset = get_products()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(
                page, many=True, context={"request": request}
            )
            total = len(queryset)
            pages = (total + self.paginator.page_size - 1) // self.paginator.page_size
            return self.get_paginated_response(
                {
                    "items": serializer.data,
                    "total": total,
                    "pages": pages,
                }
            )
        serializer = ProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

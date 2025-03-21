from rest_framework import viewsets
from rest_framework.response import Response
from asgiref.sync import sync_to_async, async_to_sync
from .serializers import OrderSerializer
from .models import Order

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        @async_to_sync
        async def fetch_orders():
            return await sync_to_async(list)(Order.objects.all())

        return fetch_orders()

    def create(self, request, *args, **kwargs):
        @async_to_sync
        async def perform_create_async(serializer):
            await sync_to_async(self.perform_create)(serializer)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        perform_create_async(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
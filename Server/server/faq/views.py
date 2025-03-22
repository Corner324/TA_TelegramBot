from rest_framework import viewsets
from asgiref.sync import sync_to_async, async_to_sync
from .models import FAQ
from .serializers import FAQSerializer


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FAQSerializer

    def get_queryset(self):
        @async_to_sync
        async def fetch_faqs():
            return await sync_to_async(list)(FAQ.objects.all())

        return fetch_faqs()

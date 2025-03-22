from django.urls import path
from .views import StripeWebhookView

urlpatterns = [
    path('stripe/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
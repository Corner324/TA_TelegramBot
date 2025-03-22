import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from order.models import Order
import logging

logger = logging.getLogger(__name__)

class StripeWebhookView(APIView):
    """Обработка вебхуков от Stripe."""
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            logger.error("Неверный payload")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.error("Неверная подпись")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session['metadata']['order_id']
            try:
               
                order = Order.objects.get(id=order_id)
                order.status = 'paid'
                order.save()
                logger.info(f"Заказ {order_id} успешно оплачен")
            except Order.DoesNotExist:
                logger.error(f"Заказ {order_id} не найден в базе данных")
                return Response(
                    {"error": f"Order {order_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response({"status": "success"}, status=status.HTTP_200_OK)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"error": "Telegram ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Проверяем, существует ли UserProfile с данным telegram_id
            profile = UserProfile.objects.filter(telegram_id=telegram_id).first()
            if profile:

                serializer = UserProfileSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Если профиля нет, создаём нового пользователя и профиль
            username = f"tg_{telegram_id}"
            if User.objects.filter(username=username).exists():
                return Response({"error": "User with this Telegram ID already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                username=username,
                password=None
            )
            profile = UserProfile.objects.create(
                user=user,
                telegram_id=telegram_id
            )
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
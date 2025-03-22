from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    telegram_id = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.user.username} (Telegram ID: {self.telegram_id})"

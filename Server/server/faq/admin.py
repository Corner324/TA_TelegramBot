from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("question", "answer")

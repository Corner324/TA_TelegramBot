from django.contrib import admin
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import path
from utils.message_sender import telegram_sender
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class BroadcastForm(forms.Form):
    message = forms.CharField(
        label="Сообщение для рассылки",
        widget=forms.Textarea(attrs={"rows": 5, "cols": 50}),
        help_text="Введите текст сообщения, которое будет отправлено выбранным пользователям."
    )
    selected_ids = forms.CharField(widget=forms.HiddenInput)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "telegram_id")
    actions = ["send_broadcast_action"]

    def send_broadcast_action(self, request, queryset):
        selected_ids = ",".join(str(obj.id) for obj in queryset)
        return HttpResponseRedirect(f"/admin/user/userprofile/send_broadcast/?selected_ids={selected_ids}")
    send_broadcast_action.short_description = "📢 Отправить сообщение выбранным пользователям"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("send_broadcast/", self.admin_site.admin_view(self.send_broadcast), name="send_broadcast"),
        ]
        return custom_urls + urls

    def send_broadcast(self, request):
        if request.method == "GET":
            """Исправлено: теперь рендерим форму"""
            selected_ids = request.GET.get("selected_ids", "")
            form = BroadcastForm(initial={"selected_ids": selected_ids})
            return self.render_broadcast_form(request, form)

        if request.method == "POST":
            message_text = request.POST.get("message")
            selected_ids = request.POST.get("selected_ids", "").split(",")
            users = UserProfile.objects.filter(id__in=selected_ids)

            sent_count, failed_count = 0, 0

            for user_profile in users:
                if user_profile.telegram_id:
                    success = telegram_sender.sync_send_message(user_profile.telegram_id, message_text)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1

            self.message_user(
                request,
                f"📢 Рассылка завершена: отправлено {sent_count} сообщений, "
                f"не отправлено {failed_count}.",
                level=messages.SUCCESS if sent_count > 0 else messages.WARNING
            )
            return HttpResponseRedirect(request.get_full_path())

    def render_broadcast_form(self, request, form):
        """Исправлено: Теперь рендерим шаблон формы"""
        template = loader.get_template("admin/broadcast_form.html")
        context = {"form": form}
        return HttpResponse(template.render(context, request))

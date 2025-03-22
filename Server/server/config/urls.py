from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include([
        path("", include("catalog.urls")),
        path("", include("faq.urls")),
        path("", include("order.urls")),
        path("", include("user.urls")),
    ])),
    path('webhooks/', include('webhooks.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

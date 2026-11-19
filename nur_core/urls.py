from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from .views import contact, home

urlpatterns = [
    path("", home, name="home"),
    path("a-propos/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("contact/", contact, name="contact"),
    path("contact/envoye/", contact, {"sent": True}, name="contact-sent"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
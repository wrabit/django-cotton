from . import views
from django.urls import path
from django.views.generic import TemplateView

app_name = "django_cotton"


urlpatterns = [
    path("include", TemplateView.as_view(template_name="cotton_include.html")),
    path("test/compiled-cotton", views.compiled_cotton_test_view),
    path("test/native-extends", views.native_extends_test_view),
    path("test/native-include", views.native_include_test_view),
]

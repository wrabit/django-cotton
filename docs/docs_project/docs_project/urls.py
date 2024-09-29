from . import views
from django.urls import path

urlpatterns = [
    path(
        "",
        views.build_view(
            "home", title="Django Cotton - Modern UI Composition for Django"
        ),
        name="home",
    ),
    path("docs/quickstart", views.build_view("quickstart"), name="quickstart"),
    path("docs/installation", views.build_view("installation"), name="installation"),
    path("docs/usage", views.build_view("usage"), name="usage"),
    # Features
    path("docs/components", views.build_view("components"), name="components"),
    path("docs/slots", views.build_view("slots"), name="slots"),
    path(
        "docs/attributes-and-vars",
        views.build_view("attributes_and_vars"),
        name="attributes-and-vars",
    ),
    # Examples
    path("docs/form-fields", views.build_view("form_fields"), name="form-fields"),
    path("docs/alpine-js", views.build_view("alpine_js"), name="alpine-js"),
    path("docs/layouts", views.build_view("layouts"), name="layouts"),
    path("docs/icons", views.build_view("icons"), name="icons"),
    # More
    path("docs/configuration", views.build_view("configuration"), name="configuration"),
    path(
        "docs/django-template-partials",
        views.build_view("django_template_partials"),
        name="django-template-partials",
    ),
]

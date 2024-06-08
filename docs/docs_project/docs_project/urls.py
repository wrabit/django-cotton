from . import views
from django.urls import path

urlpatterns = [
    path("", views.home, name="home"),
    path("docs/quickstart", views.build_view("quickstart"), name="quickstart"),
    path("docs/installation", views.build_view("installation"), name="installation"),
    path("docs/usage", views.build_view("usage"), name="usage"),
    # Features
    path("docs/components", views.build_view("components"), name="components"),
    path("docs/slots", views.build_view("slots"), name="slots"),
    path(
        "docs/attributes-and-props",
        views.build_view("attributes_and_props"),
        name="attributes-and-props",
    ),
    # Examples
    path("docs/layouts", views.build_view("layouts"), name="layouts"),
    path("docs/icons", views.build_view("icons"), name="icons"),
    path("docs/form-fields", views.build_view("form_fields"), name="form-fields"),
    path("docs/alpine-js", views.build_view("alpine_js"), name="alpine-js"),
    # More
    path("docs/how-it-works", views.build_view("how_it_works"), name="how-it-works"),
]

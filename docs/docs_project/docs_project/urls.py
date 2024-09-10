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
    # UI
    path("ui", views.build_view("ui_docs/getting_started"), name="ui"),
    path("ui/input", views.build_view("ui_docs/input"), name="ui-input"),
    path("ui/textarea", views.build_view("ui_docs/textarea"), name="ui-textarea"),
]

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
    path(
        "docs/usage-patterns", views.build_view("usage_patterns"), name="usage-patterns"
    ),
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
    # UI
    path("ui", views.build_view("ui_docs/getting_started"), name="ui"),
    path("ui/theming", views.build_view("ui_docs/theming"), name="ui-theming"),
    path("ui/accordion", views.build_view("ui_docs/accordion"), name="ui-accordion"),
    path("ui/badge", views.build_view("ui_docs/badge"), name="ui-badge"),
    path("ui/button", views.build_view("ui_docs/button"), name="ui-button"),
    path("ui/card", views.build_view("ui_docs/card"), name="ui-card"),
    path("ui/checkbox", views.build_view("ui_docs/checkbox"), name="ui-checkbox"),
    path("ui/datepicker", views.build_view("ui_docs/datepicker"), name="ui-datepicker"),
    path("ui/dropdown", views.build_view("ui_docs/dropdown"), name="ui-dropdown"),
    path("ui/field", views.build_view("ui_docs/field"), name="ui-field"),
    path("ui/input", views.build_view("ui_docs/input"), name="ui-input"),
    path("ui/navbar", views.build_view("ui_docs/navbar"), name="ui-navbar"),
    path("ui/radio", views.build_view("ui_docs/radio"), name="ui-radio"),
    path("ui/select", views.build_view("ui_docs/select"), name="ui-select"),
    path("ui/tabs", views.build_view("ui_docs/tabs"), name="ui-tabs"),
    path("ui/textarea", views.build_view("ui_docs/textarea"), name="ui-textarea"),
    path("ui/tooltip", views.build_view("ui_docs/tooltip"), name="ui-tooltip"),
]

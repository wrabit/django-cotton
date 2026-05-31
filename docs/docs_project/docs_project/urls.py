from . import views
from django.urls import path
from django.views.generic.base import RedirectView

urlpatterns = [
    # 301: the old "Usage Patterns" page was split into Fundamentals,
    # Attribute Proxying and Compound Components. Point the retired slug at
    # Fundamentals, which inherited the bulk of its content.
    path(
        "docs/usage-patterns",
        RedirectView.as_view(pattern_name="fundamentals", permanent=True),
    ),
    path(
        "",
        views.build_view(
            "home", title="Django Cotton - Modern UI Composition for Django"
        ),
        name="home",
    ),
    path(
        "docs/thinking-in-components",
        views.build_view(
            "thinking_in_components", title="Thinking in Components - Django Cotton"
        ),
        name="thinking-in-components",
    ),
    path("docs/quickstart", views.build_view("quickstart"), name="quickstart"),
    path("docs/fundamentals", views.build_view("fundamentals"), name="fundamentals"),
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
    path(
        "docs/htmx-examples",
        views.build_view("htmx_examples", title="HTMX Integration - Django Cotton"),
        name="htmx-examples",
    ),
    path(
        "docs/layouts",
        views.build_view("layouts", title="Composing Layouts - Django Cotton"),
        name="layouts",
    ),
    path(
        "docs/icons",
        views.build_view("icons", title="Cotton as SVG Icons - Django Cotton"),
        name="icons",
    ),
    # Usage Patterns
    path(
        "docs/variants",
        views.build_view("variants", title="Component Variants - Django Cotton"),
        name="variants",
    ),
    path(
        "docs/attribute-proxying",
        views.build_view("attribute_proxying"),
        name="attribute-proxying",
    ),
    path(
        "docs/index-component",
        views.build_view(
            "index_component", title="Compound Components - Django Cotton"
        ),
        name="index-component",
    ),
    # Demo endpoints for HTMX examples
    path("demo/tasks/<int:id>", views.demo_task_detail, name="demo-task-detail"),
    path("demo/tasks/<int:id>/edit", views.demo_task_edit, name="demo-task-edit"),
    path("demo/tasks/<int:id>/update", views.demo_task_update, name="demo-task-update"),
    path("demo/tasks/<int:id>/delete", views.demo_task_delete, name="demo-task-delete"),
    path("demo/validate-field", views.demo_validate_field, name="demo-validate-field"),
    path("demo/users/<int:id>/details", views.demo_user_details, name="demo-user-details"),
    path("demo/search", views.demo_search, name="demo-search"),
    # More
    path("docs/configuration", views.build_view("configuration"), name="configuration"),
]

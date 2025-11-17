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
    path("docs/htmx-examples", views.build_view("htmx_examples"), name="htmx-examples"),
    path("docs/layouts", views.build_view("layouts"), name="layouts"),
    path("docs/icons", views.build_view("icons"), name="icons"),
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
    path(
        "docs/django-template-partials",
        views.build_view("django_template_partials"),
        name="django-template-partials",
    ),
]

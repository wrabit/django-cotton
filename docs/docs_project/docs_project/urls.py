from . import views
from django.urls import path
from django.views.generic.base import RedirectView
from django.views.decorators.clickjacking import xframe_options_sameorigin

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
    # UI
    path("ui", views.build_view("ui_docs/home"), name="ui"),
    path("ui/installation", views.build_view("ui_docs/installation"), name="ui-installation"),
    path("ui/theming", views.build_view("ui_docs/theming"), name="ui-theming"),
    path("ui/theme-builder", views.build_view("ui_docs/themes", title="Theme Builder - Django Cotton UI"), name="ui-theme-builder"),
    path("ui/accordion", views.build_view("ui_docs/accordion"), name="ui-accordion"),
    path("ui/alert", views.build_view("ui_docs/alert"), name="ui-alert"),
    path("ui/avatar", views.build_view("ui_docs/avatar"), name="ui-avatar"),
    path("ui/badge", views.build_view("ui_docs/badge"), name="ui-badge"),
    path("ui/breadcrumbs", views.build_view("ui_docs/breadcrumbs"), name="ui-breadcrumbs"),
    path("ui/button", views.build_view("ui_docs/button"), name="ui-button"),
    path("ui/calendar", views.build_view("ui_docs/calendar"), name="ui-calendar"),
    path("ui/card", views.build_view("ui_docs/card"), name="ui-card"),
    path("ui/checkbox", views.build_view("ui_docs/checkbox"), name="ui-checkbox"),
    path("ui/collapse", views.build_view("ui_docs/collapse"), name="ui-collapse"),
    path("ui/combobox", views.build_view("ui_docs/combobox"), name="ui-combobox"),
    path("ui/composer", views.build_view("ui_docs/composer"), name="ui-composer"),
    path("ui/datepicker", views.build_view("ui_docs/datepicker"), name="ui-datepicker"),
    path("ui/dialog", views.build_view("ui_docs/dialog"), name="ui-dialog"),
    path("ui/dropdown", views.build_view("ui_docs/dropdown"), name="ui-dropdown"),
    path(
        "ui/dropdown/viewport",
        xframe_options_sameorigin(views.build_view("ui_docs/dropdown_viewport")),
        name="ui-dropdown-viewport",
    ),
    # Responsive-positioning preview pages (loaded in resizable iframes)
    path(
        "ui/combobox/viewport",
        xframe_options_sameorigin(views.build_view("ui_docs/combobox_viewport")),
        name="ui-combobox-viewport",
    ),
    path(
        "ui/select/viewport",
        xframe_options_sameorigin(views.build_view("ui_docs/select_viewport")),
        name="ui-select-viewport",
    ),
    path(
        "ui/datepicker/viewport",
        xframe_options_sameorigin(views.build_view("ui_docs/datepicker_viewport")),
        name="ui-datepicker-viewport",
    ),
    path(
        "ui/tooltip/viewport",
        xframe_options_sameorigin(views.build_view("ui_docs/tooltip_viewport")),
        name="ui-tooltip-viewport",
    ),
    path("ui/field", views.build_view("ui_docs/field"), name="ui-field"),
    path("ui/input", views.build_view("ui_docs/input"), name="ui-input"),
    path("ui/nav", views.build_view("ui_docs/nav"), name="ui-nav"),
    path("ui/navbar", views.build_view("ui_docs/navbar"), name="ui-navbar"),
    path("ui/navlist", views.build_view("ui_docs/navlist"), name="ui-navlist"),
    path("ui/pagination", views.build_view("ui_docs/pagination"), name="ui-pagination"),
    path("ui/popover", views.build_view("ui_docs/popover"), name="ui-popover"),
    path("ui/progress", views.build_view("ui_docs/progress"), name="ui-progress"),
    path("ui/radio", views.build_view("ui_docs/radio"), name="ui-radio"),
    path("ui/range", views.build_view("ui_docs/range"), name="ui-range"),
    path("ui/scrollspy", views.build_view("ui_docs/scrollspy"), name="ui-scrollspy"),
    path("ui/select", views.build_view("ui_docs/select"), name="ui-select"),
    path("ui/drawer", views.build_view("ui_docs/drawer"), name="ui-drawer"),
    path("ui/spinner", views.build_view("ui_docs/spinner"), name="ui-spinner"),
    path("ui/switch", views.build_view("ui_docs/switch"), name="ui-switch"),
    path("ui/table", views.build_view("ui_docs/table"), name="ui-table"),
    path("ui/tabs", views.build_view("ui_docs/tabs"), name="ui-tabs"),
    path("ui/textarea", views.build_view("ui_docs/textarea"), name="ui-textarea"),
    path("ui/toast", views.build_view("ui_docs/toast"), name="ui-toast"),
    path("ui/tooltip", views.build_view("ui_docs/tooltip"), name="ui-tooltip"),
]

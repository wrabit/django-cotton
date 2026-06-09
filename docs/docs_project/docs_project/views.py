from django.shortcuts import render
from django.http import HttpResponse


def snake_to_title(snake_str):
    return snake_str.replace("_", " ").title()


def build_view(template_name, title=None, description=None):
    # Derive a clean label from the leaf name (e.g. "ui_docs/navbar" -> "Navbar",
    # "form_fields" -> "Form Fields") rather than title-casing the whole path.
    label = snake_to_title(template_name.rsplit("/", 1)[-1])
    is_ui = template_name.startswith("ui_docs/")

    if title is None:
        title = f"{label} - Django Cotton UI" if is_ui else f"{label} - Django Cotton"

    if description is None:
        description = (
            f"{label} component for Django Cotton UI: an accessible, themeable component "
            f"built with Tailwind CSS and Alpine.js. Live examples and full API reference."
            if is_ui else
            f"{label} - Django Cotton: build reusable server-side UI components in single "
            f"HTML files, no Python required, fully interoperable with Django templates."
        )

    def view(request):
        context = {"meta_title": title, "meta_description": description}

        # Datepicker docs: dynamic limit dates within the current month, so the
        # disabled / min / max examples are always visible in the opened calendar.
        if template_name == "ui_docs/datepicker":
            import datetime

            ym = datetime.date.today().strftime("%Y-%m")
            context["dp_min"] = f"{ym}-09"
            context["dp_max"] = f"{ym}-20"
            context["dp_disabled_dates"] = [f"{ym}-11", f"{ym}-12", f"{ym}-18"]

        # Add demo data for HTMX examples page
        if template_name == "htmx_examples":
            context["demo_tasks"] = [
                {
                    "id": 1,
                    "title": "Implement user authentication",
                    "description": "Add login and registration functionality",
                },
                {
                    "id": 2,
                    "title": "Design homepage layout",
                    "description": "Create responsive homepage with hero section",
                },
            ]

        return render(request, f"{template_name}.html", context)

    return view


# HTMX Demo Views (stateless - just echo back data)
def demo_task_detail(request, id):
    """Display a task in read mode."""
    # In real app, this would fetch from database
    # For demo, we use default values
    title = request.GET.get("title", f"Task {id}")
    description = request.GET.get("description", f"Description for task {id}")

    return render(
        request,
        "cotton/examples/htmx/task_display.html",
        {"id": id, "title": title, "description": description},
    )


def demo_task_edit(request, id):
    """Display a task in edit mode."""
    # Get current values from query params (passed from display component)
    title = request.GET.get("title", f"Task {id}")
    description = request.GET.get("description", f"Description for task {id}")

    return render(
        request,
        "cotton/examples/htmx/task_edit.html",
        {"id": id, "title": title, "description": description},
    )


def demo_task_update(request, id):
    """Update a task and return display mode (stateless - just echo back)."""
    # Echo back the submitted data
    title = request.POST.get("title", "")
    description = request.POST.get("description", "")

    return render(
        request,
        "cotton/examples/htmx/task_display.html",
        {"id": id, "title": title, "description": description},
    )


def demo_validate_field(request):
    """Validate form field and return field component with error state."""
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    field_name = request.GET.get("field_name")
    field_value = request.POST.get(field_name, "")
    error = None

    if field_name == "email":
        try:
            validate_email(field_value)
        except ValidationError:
            error = "Invalid email address"
    elif field_name == "username" and len(field_value) < 3:
        error = "Username must be at least 3 characters"

    return render(
        request,
        "cotton/examples/htmx/form_field.html",
        {
            "name": field_name,
            "label": field_name.title(),
            "value": field_value,
            "error": error,
            "type": "email" if field_name == "email" else "text",
        },
    )


def demo_task_delete(request, id):
    """Delete task demo - return empty response to remove element."""
    return HttpResponse("", content_type="text/html")


def demo_user_details(request, id):
    """Show user details in modal."""
    # Demo data
    users = {
        1: {"name": "Alice Johnson", "email": "alice@example.com", "role": "Developer"},
        2: {"name": "Bob Smith", "email": "bob@example.com", "role": "Designer"},
        3: {"name": "Carol White", "email": "carol@example.com", "role": "Manager"},
    }

    user = users.get(id, {"name": "User", "email": "user@example.com", "role": "Unknown"})

    return render(
        request, "cotton/examples/htmx/user_details.html", user
    )


def demo_search(request):
    """Search demo - return mock results."""
    query = request.GET.get("q", "")

    # Mock search results
    all_articles = [
        {"title": "Getting Started with Django", "description": "Learn the basics of Django"},
        {"title": "HTMX and Django Integration", "description": "Build dynamic apps with HTMX"},
        {"title": "Django Cotton Components", "description": "Reusable UI components for Django"},
        {"title": "Alpine.js Guide", "description": "Lightweight JavaScript framework"},
        {"title": "Tailwind CSS Tips", "description": "Utility-first CSS framework"},
    ]

    results = [
        article for article in all_articles
        if query.lower() in article["title"].lower() or query.lower() in article["description"].lower()
    ] if query else []

    return render(
        request,
        "cotton/examples/htmx/search_results.html",
        {"results": results, "query": query},
    )

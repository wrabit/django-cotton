# Python API

## `render_component`

Renders a component from Python and returns the HTML. The shape follows Django's `render()`:

```python
from django_cotton import render_component

render_component(request, "button", {"label": "Save"})
render_component(request, "ui.button", label="Save", pk=123)
render_component(request, "settings.user-row", {"user": user}, extra_class="highlight")
```

- `component_name` uses the same naming as the tag: dots for folders, hyphens for underscores. `"ui.button"` is `cotton/ui/button.html`.
- `context` and keyword arguments both become attributes on the component. Keyword arguments win on a clash.
- The component renders with a `RequestContext`, so context processors apply.

The usual use is an HTMX partial:

```python
from django.http import HttpResponse
from django_cotton import render_component

def task_detail(request, id):
    task = get_object_or_404(Task, id=id)
    return HttpResponse(render_component(request, "task", id=task.id, title=task.title))
```

See [HTMX integration](htmx-examples.md).

## App configs

`django_cotton` in `INSTALLED_APPS` configures the template engine for you: it wraps the loaders in Django's cached loader with Cotton's loader first, and registers the tags as builtins. It leaves an existing cached loader setup alone if Cotton is already in it.

To configure the engine yourself, use `django_cotton.apps.SimpleAppConfig` instead and add the pieces by hand:

```python
INSTALLED_APPS = ["django_cotton.apps.SimpleAppConfig"]

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "OPTIONS": {
        "loaders": [(
            "django.template.loaders.cached.Loader",
            [
                "django_cotton.cotton_loader.Loader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        )],
        "builtins": ["django_cotton.templatetags.cotton"],
    },
}]
```

`django_cotton.cotton_loader.Loader` compiles `<c-` tags into template tags as templates load. `django_cotton.templatetags.cotton` holds the tags and filters.

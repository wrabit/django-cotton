# Quickstart

## Install Cotton

Run the following command:

```cotton language=python hide-label
pip install django-cotton
```

Then update your settings.py:

#### For automatic configuration:

```cotton language=python label=settings.py
INSTALLED_APPS = [
    'django_cotton',
]
```

This will attempt to automatically handle the settings.py by adding the required loader and templatetags.

#### For custom configuration

If your project requires any non-default loaders or you do not wish Cotton to manage your settings, you should instead provide `django_cotton.apps.SimpleAppConfig` in your INSTALLED_APPS:

```cotton language=python label=settings.py
INSTALLED_APPS = [
    'django_cotton.apps.SimpleAppConfig',
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        ...
        "OPTIONS": {
            "loaders": [(
                "django.template.loaders.cached.Loader",
                [
                    "django_cotton.cotton_loader.Loader",
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            )],
            "builtins": [
                "django_cotton.templatetags.cotton"
            ],
        }
    }
]
```

## Create a component

Create a new directory in your templates directory called `cotton`. Inside this directory create a new file called `card.html` with the following content:

```cotton label=templates/cotton/card.html
<div class="bg-white shadow rounded border p-4">
    <h2>{{ title }}</h2>
    <p>{{ slot }}</p>
    <button href="{% url url %}">Read more</button>
</div>
```

## Templates location

Cotton supports 2 common approaches regarding the location of the `templates` directory:

- **App level** - You can place your cotton folder in any of your installed app folders, like: `[project]/[app]/templates/cotton/row.html`
- **Project root** - You can place your cotton folder in a project level templates directory, like: `[project]/templates/cotton/row.html` (`[project]` location is provided by `BASE_DIR` if present or you may set it with `COTTON_BASE_DIR`)

Any style will allow you to include your component the same way.

## Include a component

```cotton language=python label=views.py
def dashboard_view(request):
    return render(request, "dashboard.html")
```

```cotton label=templates/dashboard.html
<c-card title="Trees" url="trees">
    We have the best trees
</c-card>

<c-card title="Spades" url="spades">
    The best spades in the land
</c-card>
```

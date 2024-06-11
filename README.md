# Cotton

Bringing component-based design to Django templates.

<a href="https://django-cotton.com" target="_blank">Document site</a>

## Overview
Cotton enhances Django templates by allowing component-based design, making UI composition more efficient and reusable. It integrates seamlessly with Tailwind CSS and retains full compatibility with native Django template features.

## Key Features
- **Rapid UI Composition:** Efficiently compose and reuse UI components.
- **Tailwind CSS Harmony:** Integrates with Tailwind's utility-first approach.
- **Interoperable with Django:** Enhances Django templates without replacing them.
- **Semantic Syntax:** HTML-like syntax for better code editor support.
- **Minimal Overhead:** Compiles to native Django components with automatic caching.

## Getting Started

### Installation
To install Cotton, run the following command:

```bash
pip install django-cotton
```

Then update your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_cotton',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['your_project/templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'loaders': [
                'django_cotton.cotton_loader.Loader',
                # continue with default loaders:
                # "django.template.loaders.filesystem.Loader",
                # "django.template.loaders.app_directories.Loader",
            ],
            'builtins': [
                'django_cotton.templatetags.cotton',
            ],
        },
    },
]
```

### Quickstart
Create a new directory in your templates directory called `cotton`. Inside this directory, create a new file called `card.cotton.html` with the following content:

```html
<div class="bg-white shadow rounded border p-4">
    <h2>{{ title }}</h2>
    <p>{{ slot }}</p>
    <button href="{% url url %}">Read more</button>
</div>
```

Create a view with a template. Views that contain Cotton components must also use the `.cotton.html` extension:

```python
# views.py
def dashboard_view(request):
    return render(request, "dashboard.cotton.html")
```

```html
<!-- templates/dashboard.cotton.html -->
<c-card title="Trees" url="trees">
    We have the best trees
</c-card>

<c-card title="Spades" url="spades">
    The best spades in the land
</c-card>
```

### Usage Basics
- **Template Extensions:** View templates including Cotton components should use the `.cotton.html` extension.
- **Component Placement:** Components should be placed in the `templates/cotton` folder.
- **Naming Conventions:** 
  - Component filenames use snake_case: `my_component.cotton.html`
  - Components are called using kebab-case: `<c-my-component />`

### Example
A minimal example using Cotton components:

```html
<!-- my_component.cotton.html -->
{{ slot }}

<!-- my_view.cotton.html -->
<c-my-component>
    <p>Some content</p>
</c-my-component>
```

### Attributes and Slots
Components can accept attributes and named slots for flexible content and behavior customization:

```html
<!-- weather.cotton.html -->
<p>It's {{ temperature }}<sup>{{ unit }}</sup> and the condition is {{ condition }}.</p>

<!-- view.cotton.html -->
<c-weather temperature="23" unit="c" condition="windy"></c-weather>
```

#### Passing Variables
To pass a variable from the parent's context, prepend the attribute with a `:`.

```html
<!-- view.cotton.html -->
<c-weather :unit="unit"></c-weather>
```

#### Named Slots
```html
<!-- weather_card.cotton.html -->
<div class="flex ...">
    <h2>{{ day }}:</h2> {{ icon }} {{ label }}
</div>

<!-- view.cotton.html -->
<c-weather-card day="Tuesday">
    <c-slot name="icon">
        <svg>...</svg>
    </c-slot>
    <c-slot name="label">
        <h2 class="text-yellow-500">Sunny</h2>
    </c-slot>
</c-weather-card>
```

### Changelog

v0.9.1 (2024-06-08) - Initial release  
v0.9.2 (2024-06-08) - Readme update  
v0.9.3 (2024-06-09) - Fixed loader docs + readme   
v0.9.4 (2024-06-11) - Added boolean attributes   
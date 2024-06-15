# Cotton

Bringing component-based design to Django templates.

- <a href="https://django-cotton.com" target="_blank">Document site</a>

Cotton aims to overcome certain limitations that exist in the django template system that hold us back when we want to apply modern practises to compose UIs in a modular and reusable way.

### Limitations applying modern UI composition to Django

| Subject                              | Limitation                                                                                        | Cotton's Solution                                                                                                                  |
|--------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| **{% include %}**                    | Designed for simple partial inclusion. Can pass variables and string arguments but not HTML.      | Highly configurable components with the ability to pass values, variables, and HTML to the component.                              |
| **{% block %} + {% extends %}**      | Forces tight coupling between templates limiting reusability. Can pass HTML but not variables.    | Cotton components are modular, can be reused anywhere, and allow passing both variables and HTML.                                  |
| **Unsemantic hierarchy**             | Block                                                                                             | HTML-like syntax for better code editor support, clearer comprehension of hierarchy.                                               |
| **Custom components**                | Components must be manually registered or included, adding overhead to development.               | Cotton components are auto-discovered, available immediately using the `<c-` syntax, streamlining the development process.         |
| **Limited default attribute values** | Django templates do not provide a way to set default attribute values within the template itself. | Cotton allows setting default attribute values using `<c-props>`, enhancing component flexibility and reducing backend complexity. |


## Walkthrough

```html
<!-- button.cotton.html -->
<a href="/" class="...">I'm a static button</a>
```
```html
<!-- template -->
<c-button />
```

An unlikely example but it shows we can use cotton like an include tag. Let's make this more useful:

```html
<!-- button.cotton.html -->
<a href="/" class="...">{{ slot }}</a>
```
```html
<!-- template -->
<c-button>Contact</c-button>
```

### Add attributes

```html
<!-- button.cotton.html -->
<a href="{{ url }}" class="...">
    {{ slot }}
</a>
```
```html
<!-- template -->
<c-button url="/contact">Contact</c-button>
```

### Utilize named slots

Named slots are a powerful concept. It allows us to provide HTML to appear in one or more areas in the component. Here we allow the button to optionally display an icon: 

```html
<!-- button.cotton.html -->
<a href="{{ url }}" class="...">
    {{ slot }}
  
    {% if icon %} 
        {{ icon }} 
    {% endif %}
</a>
```
```html
<!-- template -->
<c-button url="/contact">
    Contact
    <c-slot name="icon">
        <svg>...</svg>
    </c-slot>
</c-button>
```

### Pass template variable as an attribute

To pass a template variable you prepend the attribute name with a colon `:`

```html
<!-- button.cotton.html -->
<a href="{{ url }}" class="...">
  {{ slot }} <strong>{{ click_count }}</strong>
</a>
```
```html
<!-- template -->
<c-button :click_count="click_count">Contact</c-button>
```

You are effectively passing the variable by reference. You could achieve a similar thing by using a named slot, which will be passing the value of the variable instead:

```html
<!-- template -->
<c-button>
  Contact
  <c-slot name="click_count">
    {{ click_count }}
  </c-slot>
</c-button>
```
To demonstrate another example of passing a variable by reference, consider a bio card component:

```html
<!-- template -->
<c-bio-card :user="user" />
```

That has a component definiton like:

```html
<!-- bio_card.cotton.html -->
<div class="...">
  <img src="{{ user.avatar }}" alt="...">
  {{ user.username }} {{ user.country_code }}
</div>
```

### Add boolean attribute

Boolean attributes reduce boilerplate when we just want to indicate a certain attribute should be `True` or not.

```html
<!-- template -->
<c-button url="/contact" external>Contact</c-button>
```
By passing just the attribute name without a value, it will automatically be provided to the component as `True`

```html
<!-- button.cotton.html -->
<a href="{{ url }}" {% if external %} target="_blank" {% endif %} class="...">
    {{ slot }}
</a>
```

### Default attribute values with `<c-props>`

Django templates adhere quite strictly to the MVC model and does not permit much data control in the View. But what if we want to handle data for the purpose of UI state only? Having this in the back would surely convolute the backend code. For this, Cotton can set simple attribute values that help us decide on sensible defaults for our components.

```html
<!-- button.cotton.html -->
<c-props theme="bg-purple-500" />

<a href="..." class="{{ theme }}">
    {{ slot }}
</a>
```
```html
<!-- template -->
<c-button>I'm a purple button</c-button>
```

Now we have a default theme for our button, but it is overridable:

```html
<!-- template -->
<c-button theme="bg-green-500">But I'm green</c-button>
```

## Key Features
- **Rapid UI Composition:** Efficiently compose and reuse UI components.
- **Tailwind CSS Harmony:** Integrates with Tailwind's utility-first approach.
- **Interoperable with Django:** Enhances Django templates without replacing them.
- **Semantic Syntax:** HTML-like syntax for better code editor support.
- **Minimal Overhead:** Compiles to native Django components with automatic caching.


## Installation
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

## Usage Basics
- **File Extensions:** Views templates that contain Cotton and Cotton components themselves should use the `.cotton.html` extension.
- **Component Placement:** Components should be placed in the `templates/cotton` folder.
- **Naming Conventions:** 
  - Component filenames use snake_case: `my_component.cotton.html`
  - Components are called using kebab-case: `<c-my-component />`

### Changelog

v0.9.1 (2024-06-08) - Initial release  
v0.9.2 (2024-06-08) - Readme update  
v0.9.3 (2024-06-09) - Fixed loader docs + readme   
v0.9.4 (2024-06-11) - Added boolean attributes   


### Existing limitations
Modern component-based frameworks provide multiple ways to customise components. One powerful option is passing HTML to appear in one or more areas in the component. Whilst the `{% include %}` lets us include a template and provide template variables and strings, it’s not possible to provide HTML.


Design for rapid UI composition
- cotton features html-like syntax. Code editors and IDE's recognise these as html tags so you get syntax highlighting and auto-completion out of the box
- components don't need a data component or class
- components are auto discovered, you create file and immediately available using the <c- syntax
- 
# Cotton

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Bringing component-based design to Django templates.

- <a href="https://django-cotton.com" target="_blank">Document site</a>

Cotton aims to overcome certain limitations that exist in the django template system that hold us back when we want to apply modern practises to compose UIs in a modular and reusable way.

## Key Features
- **Modern UI Composition:** Efficiently compose and reuse UI components.
- **Interoperable with Django:** Cotton compliments django's existing templates.
- **HTML-like Syntax:** Better code editor support as component tags are similar to html tags.
- **Minimal Overhead:** Compiles to native Django components with dynamic caching.
- **Tailwind CSS:** Integrates well with Tailwind's utility-class approach.

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

## Usage Basics
- **File Extensions:** Views templates that contain Cotton and Cotton components themselves should use the `.cotton.html` extension.
- **Component Placement:** Components should be placed in the `templates/cotton` folder.
- **Naming Conventions:** 
  - Component filenames use snake_case: `my_component.cotton.html`
  - Components are called using kebab-case: `<c-my-component />`

## Changelog
 
v0.9.1 (2024-06-08) - Initial open source release  
v0.9.2 (2024-06-08) - Readme update  
v0.9.3 (2024-06-09) - Fixed loader docs + readme   
v0.9.4 (2024-06-11) - Added boolean attributes
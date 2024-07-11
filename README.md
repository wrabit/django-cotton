<img alt="Django Cotton Logo" src="https://github.com/wrabit/django-cotton/assets/5918271/1b0de6be-e943-4250-84c5-4662e2be07f5" width="400">

<!--<img src="https://github.com/wrabit/django-cotton/assets/5918271/e1c204dd-a91d-4883-8b76-b47af264c251" width="400">-->

# Django Cotton

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Bringing component-based design to Django templates.

- Docs site + demos: <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>

## Contents

[Why?](#why-cotton)  
[Your First component](#your-first-component)  
[Attributes](#add-attributes)  
[Names Slots](#add-attributes)  
[Pass Template Variables](#pass-template-variable-as-an-attribute)  
[Template expressions in attributes](#template-expressions-inside-attributes)  
[Boolean attributes](#boolean-attributes)  
[Passing Python data types](#passing-python-data-types)  
[In-component Variables with `<c-vars>`](#in-component-variables-with-c-vars)  
[Increase Re-usability with `{{ attrs }}`](#increase-re-usability-with--attrs-)  
[HTMX Example](#an-example-with-htmx)  
[Usage Basics](#usage-basics)  
[Limitations in Django that Cotton overcomes](#limitations-in-django-that-cotton-overcomes)  
[Caching](#caching)  
[Changelog](#changelog)  


## Why Cotton?

Cotton aims to overcome [certain limitations](#limitations-in-django-that-cotton-overcomes) that exist in the django template system that hold us back when we want to apply modern practises to compose UIs in a modular and reusable way.

## Key Features
- **Modern UI Composition:** Efficiently compose and reuse UI components.
- **Interoperable with Django:** Cotton enhances django's existing template system.
- **HTML-like Syntax:** Better code editor support and productivity as component tags are similar to html tags.
- **Minimal Overhead:** Compiles to native Django components with dynamic caching.
- **Encapsulates UI:** Keep layout, design and interaction in one file (especially when paired with Tailwind and Alpine.js)
- **Compliments HTMX:** Create smart components, reducing repetition and enhancing maintainability.

## Walkthrough

### Your first component

```html
<!-- cotton/button.html -->
<a href="/" class="...">{{ slot }}</a>
```
```html
<!-- in view -->
<c-button>Contact</c-button>
```
```html
<!-- output -->
<a href="/" class="...">Contact</a>
```

Everything provided between the opening and closing tag is provided to the component as `{{ slot }}`. It can contain any HTML and any Django template expressions.

### Add attributes

```html
<!-- cotton/button.html -->
<a href="{{ url }}" class="...">
    {{ slot }}
</a>
```
```html
<!-- in view -->
<c-button url="/contact">Contact</c-button>
```
```html
<!-- output -->
<a href="/contact" class="...">
    Contact
</a>
```

### Named slots

Named slots are a powerful concept. It allows us to provide HTML to appear in one or more areas in the component. Here we allow the button to optionally display an icon: 

```html
<!-- cotton/button.html -->
<a href="{{ url }}" class="...">
    {{ slot }}
  
    {% if icon %} 
        {{ icon }} 
    {% endif %}
</a>
```
```html
<!-- in view -->
<c-button url="/contact">
    Contact
    <c-slot name="icon">
        <svg>...</svg>
    </c-slot>
</c-button>
```

Named slots can also contain any django native template logic:

```html
<!-- in view -->
<c-button url="/contact">
    <c-slot name="icon">
      {% if mode == 'edit' %}
          <svg id="pencil">...</svg>
      {% else %}
          <svg id="disk">...</svg>
      {% endif %}
    </c-slot>
</c-button>
```

### Pass template variable as an attribute

To pass a template variable you prepend the attribute name with a colon `:`. Consider a bio card component:

```html
<!-- in view -->
<c-bio-card :user="user" />
```

That has a component definition like:

```html
<!-- cotton/bio_card.html -->
<div class="...">
  <img src="{{ user.avatar }}" alt="...">
  {{ user.username }} {{ user.country_code }}
</div>
```


### Template expressions inside attributes

You can use template expression statements inside attributes.

```html
<c-weather icon="fa-{{ icon }}"
           unit="{{ unit|default:'c' }}"
           condition="very {% get_intensity %}"
/>
```

### Boolean attributes

Boolean attributes reduce boilerplate when we just want to indicate a certain attribute should be `True` or not.

```html
<!-- in view -->
<c-button url="/contact" external>Contact</c-button>
```
By passing just the attribute name without a value, it will automatically be provided to the component as `True`

```html
<!-- cotton/button.html -->
<a href="{{ url }}" {% if external %} target="_blank" {% endif %} class="...">
    {{ slot }}
</a>
```

### Passing Python data types

Using the ':' to prefix an attribute tells Cotton we're passing a dynamic type down. We already know we can use this to send a variable, but you can also send basic python types, namely:

- Integers and Floats
- None, True and False
- Lists
- Dictionaries

This benefits a number of use-cases, for example if you have a select component that you want to provide the possible options from the parent:

```html
<!-- cotton/select.html -->
<select {{ attrs }}>
    {% for option in options %}
        <option value="{{ option }}">{{ option }}</option>
    {% endfor %}
</select>
```

```html
<c-select name="q1" :options="['yes', 'no', 'maybe']" />
```

```html
<!-- cotton/output -->
<select name="q1">
    <option value="yes">yes</option>
    <option value="no">no</option>
    <option value="maybe">maybe</option>
</select>
```

### Increase Re-usability with `{{ attrs }}`

`{{ attrs }}` is a special variable that contains all the attributes passed to the component in an key="value" format. This is useful when you want to pass all attributes to a child element. For example, you have inputs that can have any number of attributes defined:

```html
<!-- cotton/input.html -->
<input type="text" class="..." {{ attrs }} />
```

```html
<!-- example usage -->
<c-input placeholder="Enter your name" />
<c-input name="country" id="country" value="Japan" />
<c-input class="highlighted" required />
```

### In-component Variables with `<c-vars>`

Django templates adhere quite strictly to the MVC model and does not permit a lot of data manipulation in views. Fair enough, but what if we want to handle data for the purpose of UI state only? Having presentation related variables defined in the back is overkill and can quickly lead to higher maintenance cost and loses encapuslation of the component. Cotton allows you define in-component variables for the following reasons:

#### 1. Using `<c-vars>` for default attributes

In this example we have a button component with a default "theme" but it can be overridden.

```html
<!-- cotton/button.html -->
<c-vars theme="bg-purple-500" />

<a href="..." class="{{ theme }}">
    {{ slot }}
</a>
```
```html
<!-- in view -->
<c-button>I'm a purple button</c-button>
```
```html
<!-- output -->
<a href="..." class="bg-purple-500">
    I'm a purple button
</a>
```

Now we have a default theme for our button, but it is overridable:

```html
<!-- in view -->
<c-button theme="bg-green-500">But I'm green</c-button>
```
```html
<!-- output -->
<a href="..." class="bg-green-500">
    But I'm green
</a>
```

#### 2. Using `<c-vars>` to govern `{{ attrs }}`

Using `{{ attrs }}` to pass all attributes from parent scope onto an element in the component, you'll sometimes want to provide additional properties to the component which are not intended to be an attributes. In this case you can declare them in `<c-vars />` and it will prevent it from being in `{{ attrs }}`

Take this example where we want to provide any number of attributes to an input but also an icon setting which is not intened to be an attribute on `<input>`:

```html
<!-- in view -->
<c-input type="password" id="password" icon="padlock" />
```
```html
<!-- cotton/input.html -->
<c-vars icon />

<img src="icons/{{ icon }}.png" />

<input {{ attrs }} />
```

Input will have all attributes provided apart from the `icon`:

```html
<input type="password" id="password" />
```

### An example with HTMX

Cotton helps carve out re-usable components, here we show how to make a re-usable form, reducing code repetition and improving maintainability:

```html
<!-- cotton/form.html -->
<div id="result" class="..."></div>

<form {{ attrs }} hx-target="#result" hx-swap="outerHTML">
    {{ slot }}
    <button type="submit">Submit</button>
</form>
```

```html
<!-- in view -->
<c-form hx-post="/contact">
    <input type="text" name="name" placeholder="Name" />
    <input type="text" name="email" placeholder="Email" />
    <input type="checkbox" name="signup" />
</c-form>

<c-form hx-post="/buy">
    <input type="text" name="type" />
    <input type="text" name="quantity" />
</c-form>
```

## Usage Basics
- **Component Placement:** Components should be placed in the `templates/cotton` folder.
- **Naming Conventions:** 
  - Component filenames use snake_case: `my_component.html`
  - Components are called using kebab-case: `<c-my-component />`
 
For full docs and demos, checkout <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>


## Limitations in Django that Cotton overcomes

### HTML in attributes
❌ **Django native:**
```html
{% my_component header="<h1>Header</h1>" %}
```
✅ **Cotton:**
```html
<c-my-component>
    <c-slot name="header">
        <h1>Header</h1>
    </c-slot>
</c-my-component>
```

### Template expressions in attributes
❌ **Django native:**
```html
{% my_component model="todos.{{ index }}.name" extra="{% get_extra %}" %}
```
✅ **Cotton:**
```html
<c-my-component model="todos.{{ index }}.name" extra="{% get_extra %} />
```

### Pass simple python types
❌ **Django native:**
```html
{% my_component default_options="['yes', 'no', 'maybe']" %}
{% my_component config="{'open': True}" %}
```
✅ **Cotton:**
```html
<c-my-component :default_options="['yes', 'no', 'maybe']" />
<c-my-component :config="{'open': True}" />
```

### Multi-line definitions
❌ **Django native:** 
```html
{% my_component
    arg=1 %}
```
✅ **Cotton:**
```html
<c-my-component
    class="blue"
    x-data="{
        something: 1
    }" />
```

## Caching

Cotton components are cached whilst in production (`DEBUG = False`). The cache's TTL is for the duration of your app's lifetime. So on deployment, when the app is normally restarted, caches are cleared. During development, changes are detected on every component render. This feature is a work in progress and some refinement is planned.


## Changelog

| Version    | Date                                 | Title and Description                                                                                                                                                        |
|------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v0.9.16    | 2024-07-10                           | **Cotton Component Caching**<br>Cotton components are now cached whilst in production / `DEBUG = False`. LRU cache type with a record count of 1024, cleared on app restart. |
| v0.9.15    | 2024-07-06 &nbsp;&nbsp;&nbsp;&nbsp;  | **Hyphen to Underscore Conversion**<br>Converts variable names with hyphens to underscores for attribute access. i.e. `<c-component x-data="{}" />` -> `{{ x_data }}`        |
| v0.9.14    | 2024-07-05                           | **c-vars Optimization**<br>Optimizes `c-vars` processing for performance, yielding a 15% speed improvement in component rendering.                                           |
| v0.9.13    | 2024-07-05                           | **Multi-line Attribute Support**<br>Enables multi-line values in attributes, allowing more support for js-expression style attributes like in alpine.js                      |
| v0.9.12    | 2024-07-03                           | **Dropped ".cotton.html" Requirement**<br>Cotton no longer requires the `.cotton.html` suffix on component or view templates. A simple `.html` will do.                      |
| v0.9.11    | 2024-06-24                           | **Attribute Ordering Fix**<br>Attribute ordering was not being kept during compilation which was breaking situations when using template expressions inside tags.            |
| v0.9.10    | 2024-06-22                           | **Template Expression Attributes**<br>Ensures that the new template expression attributes are also provided in `{{ attrs }}` alongside all normal attributes.                |
| v0.9.9     | 2024-06-22                           | **Native Tags in Attributes**<br>Cotton now allows you to include template variables inside attributes. Added expression attributes to `{{ attrs }}`.                        |
| v0.9.7     | 2024-06-21                           | **Dynamic Type Attributes**<br>Using the `:` to prefix an attribute tells Cotton we're passing a dynamic type down. You can also send basic Python types.                    |
| v0.9.6     | 2024-06-17                           | **Rename c-props to c-vars**<br>Rename c props, all `<c-props />` are now `<c-vars />`.                                                                                      |
| v0.9.4     | 2024-06-11                           | **Boolean Attributes**<br>Support for Boolean attributes added with docs update.                                                                                             |
| v0.9.1     | 2024-06-08                           | **Open Source Release**<br>Open source release.                                                                                                                              |

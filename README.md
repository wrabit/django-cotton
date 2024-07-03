# Django Cotton

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

Bringing component-based design to Django templates.

- Docs + demos: <a href="https://django-cotton.com" target="_blank">django-cotton.com</a>
- <a href="https://github.com/wrabit/django-cotton/releases">Changelog</a>

## Contents

[Why?](#why-cotton)  
[Your First component](#your-first-component)  
[Attributes](#add-attributes)  
[Names Slots](#add-attributes)  
[Pass Template Variables](#pass-template-variable-as-an-attribute)  
[Template expressions in attributes](#template-expressions-inside-attributes)  
[Boolean attributes](#boolean-attributes)  
[Passing Python data types](#passing-python-data-types)  
[Default attributes](#default-attributes-with-c-vars)  
[Increase Re-usability with `{{ attrs }}`](#increase-re-usability-with--attrs-)  
[HTMLX Example](#an-example-with-htmlx)  
[Usage Basics](#usage-basics)  
[Changelog](#changelog)


## Why Cotton?

Cotton aims to overcome certain limitations that exist in the django template system that hold us back when we want to apply modern practises to compose UIs in a modular and reusable way.

## Key Features
- **Modern UI Composition:** Efficiently compose and reuse UI components.
- **Interoperable with Django:** Cotton enhances django's existing template system.
- **HTML-like Syntax:** Better code editor support and productivity as component tags are similar to html tags.
- **Minimal Overhead:** Compiles to native Django components with dynamic caching.
- **Ideal for Tailwind usage:** Helps encapsulate content and style in one file.
- **Compliments HTMX:** Create smart components, reducing repetition and enhancing maintainability.


## Walkthrough

### Your first component

```html
<!-- cotton/button.html -->
<a href="/" class="...">{{ slot }}</a>
```
```html
<!-- template -->
<c-button>Contact</c-button>
```
```html
<!-- output -->
<a href="/" class="...">Contact</a>
```

Everything provided between the opening and closing tag is provided to the component as `{{ slot }}`. It can contain HTML and any Django template expression.

### Add attributes

```html
<!-- cotton/button.html -->
<a href="{{ url }}" class="...">
    {{ slot }}
</a>
```
```html
<!-- template -->
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
<!-- template -->
<c-button url="/contact">
    Contact
    <c-slot name="icon">
        <svg>...</svg>
    </c-slot>
</c-button>
```

Named slots can also contain any django native template logic:

```html
<!-- template -->
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
<!-- template -->
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
<!-- template -->
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

### Default attributes with `<c-vars>`

Django templates adhere quite strictly to the MVC model and does not permit a lot of data manipulation in the View. Fair enough, but what if we want to handle data for the purpose of UI state only? Having this in the back would surely convolute the backend code. For this, Cotton can set simple attribute values that help allow us to set default values for our component attributes.

```html
<!-- cotton/button.html -->
<c-vars theme="bg-purple-500" />

<a href="..." class="{{ theme }}">
    {{ slot }}
</a>
```
```html
<!-- template -->
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
<!-- template -->
<c-button theme="bg-green-500">But I'm green</c-button>
```
```html
<!-- output -->
<a href="..." class="bg-green-500">
    But I'm green
</a>
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

If you combine this with the `c-vars` tag, any property defined there will be excluded from `{{ attrs }}`. For example:

```html
<!-- cotton/input.html -->
<c-vars type="text" />

<input {{ attrs }} class="..." />
```

```html
<!-- example usage -->
<c-input type="password" placeholder="Password" />
<!-- `type` will not be in {{ attrs }} -->
```

### An example with HTMLX

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
<!-- template -->
<c-form hx-post="/contact">
    <input type="text" name="name" placeholder="Name" />
    <input type="text" name="email" placeholder="Email" />
    <input type="checkbox" name="signup" />
</c-form>

<c-form url="/buy">
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


## Changelog

| Date       | Version | Title and Description                                                                                                                                                                                  |
|------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2024-06-24 | v0.9.11 | **Attribute Ordering Fix**<br><small>Attribute ordering was not being kept during compilation which was breaking situations when using template expressions to govern attributes in HTML tags.</small> |
| 2024-06-22 | v0.9.10 | **Template Expression Attributes**<br><small>Ensures that the new template expression attributes are also provided in `{{ attrs }}` alongside all normal attributes.</small>                           |
| 2024-06-22 | v0.9.9  | **Native Tags in Attributes**<br><small>Cotton now allows you to include template variables inside attributes. Added expression attributes to `{{ attrs }}`.</small>                                   |
| 2024-06-21 | v0.9.7  | **Dynamic Type Attributes**<br><small>Using the `:` to prefix an attribute tells Cotton we're passing a dynamic type down. You can also send basic Python types.</small>                               |
| 2024-06-17 | v0.9.6  | **Rename c-props to c-vars**<br><small>Rename c props, all `<c-props />` are now `<c-vars />`.</small>                                                                                                 |
| 2024-06-11 | v0.9.4  | **Boolean Attributes**<br><small>Support for Boolean attributes added with docs update.</small>                                                                                                        |
| 2024-06-08 | v0.9.1  | **Open Source Release**<br><small>Open source release.</small>                                                                                                                                         |

# Django Cotton

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

**Whilst we are still in 0.9.x versions, there could be breaking changes.**

Bringing component-based design to Django templates.

- <a href="https://django-cotton.com" target="_blank">Document site</a>

Cotton aims to overcome certain limitations that exist in the django template system that hold us back when we want to apply modern practises to compose UIs in a modular and reusable way.

## Key Features
- **Modern UI Composition:** Efficiently compose and reuse UI components.
- **Interoperable with Django:** Cotton enhances django's existing template system.
- **HTML-like Syntax:** Better code editor support and productivity as component tags are similar to html tags.
- **Minimal Overhead:** Compiles to native Django components with dynamic caching.
- **Ideal for Tailwind usage:** Helps encapsulate content and style in one file.
- **Compliments HTMX:** Create smart components, reducing repetition and enhancing maintainability.

## Walkthrough

```html
<!-- button.cotton.html -->
<a href="/" class="...">I'm a static button</a>
```
```html
<!-- template -->
<c-button />
```
```html
<!-- output -->
<a href="/" class="...">I'm a static button</a>
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
```html
<!-- output -->
<a href="/" class="...">Contact</a>
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
```html
<!-- output -->
<a href="/contact" class="...">
    Contact
</a>
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

### Using template variables in attributes

Cotton allows you to include template variables inside attributes.

```html
<c-weather icon="fa-{{ icon }}"
           unit="{{ unit|default:'c' }}"
           condition="very {% get_intensity %}"
/>
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

That has a component definition like:

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

### Passing Python data types

Using the ':' to prefix an attribute tells Cotton we're passing a dynamic type down. We already know we can use this to send a variable, but you can also send basic python types, namely:

- Integers and Floats
- None
- True and False
- Lists
- Dictionaries

This benefits a number of use-cases, for example if you have a select component that you want to provide some value:

```html
<!-- select.cotton.html -->
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
<!-- output -->
<select name="q1">
    <option value="yes">yes</option>
    <option value="no">no</option>
    <option value="maybe">maybe</option>
</select>
```

### Default attributes with `<c-vars>`

Django templates adhere quite strictly to the MVC model and does not permit much data control in the View. But what if we want to handle data for the purpose of UI state only? Having this in the back would surely convolute the backend code. For this, Cotton can set simple attribute values that help allow us to set default values for our component attributes.

```html
<!-- button.cotton.html -->
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

### Create flexible, re-usable inputs with `{{ attrs }}`

`{{ attrs }}` is a special variable that contains all the attributes passed to the component in an key="value" format. This is useful when you want to pass all attributes to a child element. For example, you have inputs that can have any number of attributes defined:

```html
<!-- input.cotton.html -->
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
<!-- input.cotton.html -->
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
<!-- form.cotton.html -->
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
- **File Extensions:** Views templates that contain Cotton and Cotton components themselves should use the `.cotton.html` extension.
- **Component Placement:** Components should be placed in the `templates/cotton` folder.
- **Naming Conventions:** 
  - Component filenames use snake_case: `my_component.cotton.html`
  - Components are called using kebab-case: `<c-my-component />`

## Changelog
 
v0.9.1 - Initial open source release  
v0.9.2 - Readme update  
v0.9.3 - Fixed loader docs + readme   
v0.9.4 - Added boolean attributes  
v0.9.5 - Minor fixes  
v0.9.6 - Renamed `c-props` to `c-vars`  
v0.9.7 - Allowed python types to be sent as attribute values  
v0.9.9 - Allow template expressions inside attributes  
v0.9.10 - Template expression attributes are now in {{ attrs }}

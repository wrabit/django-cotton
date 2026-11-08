# Reusable Form Inputs

## Building a re-usable form input field {#inputs}

Componentizing form fields enables you to easily maintain a consistent style across your whole app. This approach is particularly favourable when using a utility first CSS design system like Tailwind where every aspect of the style is detailed and maintained in isolated component files.

For this example, we're using Tailwind for styling. Let's start with a standard input:

```html label=form_view.html preview=demo.inputs.basic
<input type="text" name="shoe_size" placeholder="Shoe Size" class="border rounded shadow px-3 py-1.5">
```

Having to repeat this code more than once may get tedious and difficult to maintain. Let's componentize.

```html label=cotton/input.html
<input type="text" name="{{ name }}" placeholder="{{ placeholder }}" class="border rounded shadow px-3 py-1.5">
```

```html label=form_view.html preview=demo.inputs.multiple
<c-input name="shoe_size" placeholder="Shoe Size" />
<c-input name="country" placeholder="Country" />
<c-input name="age" placeholder="Age" />
```

## Change the input type {#type}

You will probably need more than just a text input in your project. So let's declare an attribute `type` in `<c-vars />`. Adding it as a var will allow us to set "text" as the default. Additionally, it will be excluded from `{{ attrs }}`:

```html label=cotton/input.html
<c-vars type="text" />

<input type="{{ type }}" {{ attrs }} class="border rounded shadow px-3 py-1.5">
```

```html label=form_view.html preview=demo.inputs.types
<c-input name="some_text" placeholder="Just a text field" />
<c-input type="email" name="email" placeholder="Email" />
<c-input type="password" name="password" placeholder="Password" />
<c-input type="number" name="count" placeholder="Count" />
```

## Adding validation state {#validation}

Let's also handle displaying errors when we need to.

```html label=cotton/input.html
<c-vars type="text" errors />

<input type="{{ type }}" {{ attrs }} class="border rounded shadow px-3 py-1.5 {% if errors %}border-red-500{% endif %}">

{% if errors %}
    <div class="text-red-500 text-sm mt-1">{{ errors.as_text }}</div>
{% endif %}
```

```html label=form_view.html preview=demo.inputs.validation
<c-input name="surname" placeholder="Surname" :errors="form.surname.errors" />
```

## Bonus - Adding icons {#icons}

To take customization a step further and to demonstrate the flexibility of cotton, let's now give our input component the ability to display icons.

```html label=cotton/input.html
<c-vars type="text" leading_icon />

<div class="border rounded shadow flex items-center">
    {% if leading_icon %}
        <div class="pl-3">{{ leading_icon }}</div>
    {% endif %}

    <input type="{{ type }}" {{ attrs }} class="px-3 py-1.5 w-full">
</div>
```

```html label=form_view.html preview=demo.inputs.icons
<c-input type="text" name="username" placeholder="Username">
    <c-slot name="leading_icon">
        <svg>...</svg>
    </c-slot>
</c-input>

<c-input type="password" name="password" placeholder="Password">
    <c-slot name="leading_icon">
        <svg>...</svg>
    </c-slot>
</c-input>
```

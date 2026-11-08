# Thinking in Components

> Already comfortable with components from React, Vue, Svelte, Blade or similar? Feel free to skip ahead to the [Quickstart](quickstart.md). This page is a primer for anyone coming from vanilla Django templates.

If you've built Django sites, you've composed pages with `{% include %}`, `{% extends %}` / `{% block %}` and the occasional custom template tag. These work, but they were designed for page-level layout and value substitution, not for building small, self-contained pieces of UI you reuse and nest. That gap is what components fill.

## The Django way, and where it stops {#the-django-way}

- `{% include %}` pulls in another template, but you can only hand it flat context values. You can't pass a block of markup, or nest other pieces inside it.
- `{% extends %}` / `{% block %}` is great for one page-level skeleton, but it's single inheritance and top-down: a template fills a parent's holes, it can't be dropped in repeatedly like a widget.
- Custom template tags can encapsulate logic, but each one needs a registered Python function, even for something purely presentational.

## What is a component?

A component is a single, self-contained piece of UI that you use like an HTML tag. It bundles three things:

- **Markup**: the HTML it renders.
- **Inputs**: attributes you pass in, like `<c-card title="Welcome">`.
- **A slot**: the content you nest between its tags, which can be text, HTML or other components.

```html label=cotton/card.html
<div class="card">
    <h2>{{ title }}</h2>
    {{ slot }}
</div>
```

Now use it like a tag, passing an attribute and nesting whatever content you like, including other components:

```html label=my_view.html
<c-card title="Welcome">
    <p>Any HTML, or even <c-icon name="star" />, goes here.</p>
</c-card>
```

## The payoff

- **Reuse**: define the markup once, use it anywhere and change it in a single place.
- **Composition**: nest components inside components and pass rich content as the slot, building complex UI out of small, understandable parts.
- **Encapsulation**: a component's markup, styling and behaviour live together in one file. No Python, nothing scattered across base templates.

## Coming from DTL

The instincts you already have map directly onto components:

| When you'd reach for... | Use a component |
|---|---|
| `{% include %}` with context | A tag with attributes: `<c-card title="..." />` |
| `{% block %}` / `{% extends %}` | A `<c-slot>` for each content hole |
| A presentational custom tag | A component, just an HTML file, no Python |

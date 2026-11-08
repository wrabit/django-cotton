# Component Assets

Some components need more than markup. A tooltip wants its script, a datepicker wants its stylesheet, an Alpine component wants its `Alpine.data` definition. Where do we put them?

## The problem

The tidy answer is "in the component", so everything it needs lives in one file:

```html label=cotton/tooltip.html
<span {{ attrs }}>{{ slot }}</span>

<script src="{% static 'tooltip.js' %}"></script>
```

Use it ten times and we get ten script tags. The usual fix is to move the script into the head of the base template. Now it loads on every page, including pages without a single tooltip on them. Or we gate it behind a context variable that each view has to remember to set. Either way the component no longer owns its own dependencies.

## Portals

Cotton's answer is a portal: a named spot on the page that components can send markup to. Django renders top down, so by the time a component runs the `<head>` is long gone, but a portal gets filled in once the whole page has rendered.

Mark the spot once, usually in a layout:

```html label=cotton/layouts/base.html
<head>
    <c-portal name="head" />
</head>
```

Then the component keeps its script and sends it there with `to`:

```html label=cotton/tooltip.html
<span {{ attrs }}>{{ slot }}</span>

<c-portal to="head">
    <script src="{% static 'tooltip.js' %}"></script>
</c-portal>
```

```html label=my_view.html
<c-tooltip>Save</c-tooltip>
<c-tooltip>Cancel</c-tooltip>
<c-tooltip>Delete</c-tooltip>
```

```html label="Rendered <head>"
<head>
    <script src="/static/tooltip.js"></script>
</head>
```

Ten tooltips, one script tag, and the page only loads it when a tooltip is actually on it.

## Alpine data in one place

The same trick keeps an `Alpine.data` definition next to the markup that uses it. Without a portal we'd either inline the whole object on every instance or move it to a global JS file:

```html label=cotton/counter.html
<div x-data="counter">
    <button @click="count++">{{ slot }}</button>
    <span x-text="count"></span>
</div>

<c-portal to="head">
    <script>
        document.addEventListener('alpine:init', () => {
            Alpine.data('counter', () => ({ count: 0 }))
        })
    </script>
</c-portal>
```

Every counter on the page shares the one definition, and the component is still a single file we can drop into any project.

## Shared dependencies

Several components will often need the same library. A dropdown, a tooltip and a select might all push the same positioning script. That's fine: the same push block in different components lands once, so each component can declare what it needs and we stop keeping a list of dependencies somewhere else.

## Supporting multiple pushes {#multiple}

By default a push block renders once per page. When each use should add its own entry, like a breadcrumb trail built up by the pages that render it, add `multiple` and every push appears in render order:

```html label=cotton/layouts/base.html
<nav>
    <ol>
        <li><a href="/">Home</a></li>
        <c-portal name="breadcrumbs" />
    </ol>
</nav>
```

```html label=blog/article.html
<c-layouts.base>
    <c-portal to="breadcrumbs" multiple>
        <li><a href="{% url 'blog' %}">Blog</a></li>
        <li>{{ article.title }}</li>
    </c-portal>

    <h1>{{ article.title }}</h1>
    ...
</c-layouts.base>
```

## The rules

The short version. [c-portal](c-portal.md) in the API section has them in full.

- A push block renders once per page, however many times we use the component, and the same block in two components is rendered once too. `multiple` renders it on every use.
- A push can use anything in context. Because a block renders once, the first instance's values are the ones that land, so per-instance pushes want `multiple`.
- A push with no destination on the page is simply dropped. Partials that push to `head` are fine.
- Destinations and sources can live in ordinary templates, not only in components.

> **Performance:** in our tests, a page with a portal on adds about 0.15ms.

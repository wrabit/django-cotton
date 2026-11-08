# Portals

A component sometimes needs something that doesn't belong where the component renders: a script, a stylesheet, an `Alpine.data` definition. Django renders top down, so by the time your component runs, the `<head>` is long gone. Portals let a component send markup to a named spot anywhere else on the page, and keep everything the component needs in its own file.

## The destination {#destination}

Mark the spot once, usually in a layout:

```html label=cotton/layouts/base.html
<html>
<head>
    <c-portal name="head" />
</head>
<body>
    {{ slot }}
</body>
</html>
```

## Sending content {#sending}

Push to it from any component with `to`:

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

Three tooltips, one script tag. Pushes are unique by default: identical content sent from any number of places lands once. Differences in whitespace don't count as different.

## Using context {#context}

A push renders with the component's context, so it can use attributes and anything else in scope:

```html label=cotton/chart.html
<canvas id="chart-{{ id }}"></canvas>

<c-portal to="head">
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            drawChart("chart-{{ id }}", {{ data }});
        });
    </script>
</c-portal>
```

Two charts on a page push two different scripts, because the rendered content differs. Only pushes that come out identical are collapsed.

## Pushing from a page {#pages}

Sources don't have to be components. Here the layout renders the breadcrumb trail and each page pushes its own crumb:

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

`multiple` keeps every push rather than collapsing identical ones, which is what you want for anything list-like. Pushes keep the order they were rendered in.

## How it works {#how-it-works}

The destination renders a placeholder and sources collect their content as the page renders. When the outermost template finishes, the placeholders are swapped for what was collected. There is nothing to install or configure, and it works wherever a template is rendered: views, `render_to_string`, `render_component`, emails. A push with no destination on the page is simply dropped, so partials that push to `head` are fine.

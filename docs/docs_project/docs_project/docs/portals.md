# Portals

A component sometimes needs something that doesn't belong where the component renders: a script, a stylesheet, an `Alpine.data` definition, a modal that must sit at the end of `<body>`. Django renders top down, so by the time your component runs, the `<head>` is long gone. Portals let a component send markup to a named spot anywhere else on the page, and keep everything the component needs in its own file.

## The destination {#destination}

Mark the spot once, usually in a layout:

```html label=cotton/layouts/base.html
<html>
<head>
    <c-portal name="head" />
</head>
<body>
    {{ slot }}
    <c-portal name="end" />
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

<!-- head output -->
<script src="/static/tooltip.js"></script>
```

Three tooltips, one script tag. Pushes are unique by default: identical content sent from any number of places lands once. Differences in whitespace don't count as different.

## Keeping every push {#multiple}

When you do want each push to appear, add `multiple`:

```html label=cotton/crumb.html
<c-portal to="breadcrumbs" multiple>
    <li>{{ label }}</li>
</c-portal>
```

Pushes keep the order they were rendered in.

## Using context {#context}

A push renders with the component's context, so it can use attributes and anything else in scope:

```html label=cotton/chart.html
<canvas id="chart-{{ id }}"></canvas>

<c-portal to="end">
    <script>drawChart("chart-{{ id }}", {{ data }})</script>
</c-portal>
```

## How it works {#how-it-works}

The destination renders a placeholder and sources collect their content as the page renders. When the outermost template finishes, the placeholders are swapped for what was collected. There is nothing to install or configure, and it works wherever a template is rendered: views, `render_to_string`, `render_component`, emails.

A few things that follow from that:

- A push with no destination on the page is dropped. Rendering a partial that pushes to `head` is fine, the push just has nowhere to go.
- A destination nobody pushed to renders nothing.
- Destinations and sources can both live in ordinary templates, not only in components.
- Content is kept as written, with the whitespace around the block trimmed.

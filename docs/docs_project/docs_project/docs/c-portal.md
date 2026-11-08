# c-portal

`<c-portal>` sends markup from one place in the page to another. The destination renders a placeholder, sources add to it, and the outermost template fills it in once the page has rendered.

```html label=cotton/layouts/base.html
<head>
    <c-portal name="head" />
</head>
```

```html label=cotton/tooltip.html
<span {{ attrs }}>{{ slot }}</span>

<c-portal to="head">
    <script src="{% static 'tooltip.js' %}"></script>
</c-portal>
```

## `name`

Marks a destination. Self-closing, or an empty pair. A destination nobody pushes to renders nothing.

## `to`

Marks a source. The content between the tags is rendered with the current context and sent to the destination of that name.

- A source block renders once per page. Using the component ten times sends its block once, and the same block in two different components is sent once too. The first instance to render is the one that lands, including any values it took from context.
- A push with no destination on the page is dropped.
- Surrounding whitespace is trimmed, inner indentation is kept.

## `multiple`

Sends the block on every render instead of once, in render order:

```html
<c-portal to="breadcrumbs" multiple>
    <li>{{ article.title }}</li>
</c-portal>
```

## Where it works

Destinations and sources can be in components or in ordinary templates, including a child template pushing into a layout it extends. Resolution happens when the outermost template finishes, so it works for full pages, `render_to_string`, [`render_component`](python-api.md) and isolated components alike. Nothing to configure.

## Template tag syntax

```django
{% cotton:portal name="head" %}
{% cotton:portal to="head" %}...{% endcotton:portal %}
{% cotton:portal to="breadcrumbs" multiple %}...{% endcotton:portal %}
```

See the [Component Assets](component-assets.md) tutorial for the pattern this is built for.

# Attribute Proxying

The `:attrs` dynamic attribute enables us to create wrapper components that proxy all their attributes to an inner component:

```html label=view.html
<c-outer
    class="outer-class"
    :count="42"
    :enabled="False">
    Content passed to inner component
</c-outer>
```

```html label=cotton/outer.html
<c-inner :attrs="attrs">{{ slot }}</c-inner>
```

```html label=cotton/inner.html
{{ class }}     <!-- "outer-class" -->
{{ count }}     <!-- 42 -->
{{ enabled }}   <!-- False -->
{{ slot }}      <!-- Content passed to inner component -->
```

The attributes are passed through to the inner component with their original types preserved (strings, numbers, booleans, lists, etc.), making this pattern ideal for creating higher-order components.

This pattern is particularly useful for Django form fields, where you might create a component hierarchy that passes Django widget attributes through multiple layers while adding labels, error handling and styling at each level.

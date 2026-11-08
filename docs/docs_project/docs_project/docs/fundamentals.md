# Fundamentals

## Location

- Cotton components should be placed in the `templates/cotton` folder ('cotton' path is [configurable](/docs/configuration) using `COTTON_DIR`).
- The `templates` folder can be located in either an app-level or top-level project root folder.

## Naming

Cotton uses the following naming conventions:

- By default, component file names are in snake_case (`my_component.html`).
- kebab-case filenames (`my-component.html`) can be enabled with `COTTON_SNAKE_CASED_NAMES = False`, see [configuration](/docs/configuration).
- Components are included in templates using the kebab-case name of the component: `<c-my-component />`

## Subfolders

- Components in subfolders can be called using dot notation to represent folder levels.
- A component in `sidebar/menu/link.html` would be included with `<c-sidebar.menu.link />`

## Tag Syntax

Cotton components can be used with HTML-like syntax or native Django template tags.

### HTML-like Syntax

Cotton enables you to use html-like syntax to include your components. This tends to enhance productivity as editors and IDEs often provide autocompletion, auto closing and syntax highlighting of xml-like tags out of the box.

```html label="With content"
<c-button>
    Click me
</c-button>
```

### Native Template Tags

If you prefer using native template tags you can use Cotton's template tags.

#### HTML Syntax

```html label="HTML-like syntax" ignore-syntax-choice
<c-button title="Click me">
    Click here
</c-button>
```

#### Native Syntax

```django label="Native Django template syntax" ignore-syntax-choice
{% cotton button title="Click me" %}
    Click here
{% endcotton %}
```

### Syntax Comparison

| Feature | HTML-like Syntax | Native Template Syntax |
|---|---|---|
| Component | `<c-button>...</c-button>` | `{% cotton button %}...{% endcotton %}` |
| Self-closing Component | `<c-button />` | `{% cotton button / %}` |
| Variables | `<c-vars title />` | `{% cotton:vars title %}` |
| Named Slot | `<c-slot name="header">...</c-slot>` | `{% cotton:slot header %}...{% endcotton:slot %}` |

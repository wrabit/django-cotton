# Compound Components

A *compound component* is a parent made up of several coordinated sub-parts that are used together as a family, like a card with its own header and body. Cotton lets you build one by grouping the parts in a folder: add an `index.html` to make the folder itself usable as the default component, then address the siblings with dot notation. This also keeps your project structure tidy and cuts repetition in the template.

```text label="Project structure"
templates/
├── cotton/
│   ├── card/
│   │   ├── index.html
│   │   ├── header.html
```

```html label=Usage
<c-card>
    <c-card.header>...</c-card.header>
</c-card>
```

Here `<c-card>` resolves to `cotton/card/index.html`, while `<c-card.header>` resolves to `cotton/card/header.html`, with no extra `index` segment needed in the tag.

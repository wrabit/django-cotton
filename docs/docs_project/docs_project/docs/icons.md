# Cotton as SVG Icons

## Using custom SVG icons {#icons}

Cotton's component-ized approach provides another compelling use-case. Sure, there are svg icon packages for Django already, but what if you need to use a custom icon in your project?

> Looking for a ready-made set instead of hand-rolling your own? [cotton-icons](https://pypi.org/project/cotton-icons/) ([GitHub](https://github.com/wrabit/cotton-icons)) ships thousands of icons as drop-in Cotton components, and already covers **Heroicons**, **Tabler Icons** and **Lucide**.

```html label=plane.svg preview=demo.icons.plane-svg
<svg viewBox="0 0 512 512">
  <g fill="none" stroke="#000" stroke-width="30" stroke-linejoin="round">
    <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
    <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
    <path d="M143.533 256 497 127.467l-241 241z"/>
  </g>
</svg>
```

## Let's cotton-ize {#cottonizing}

```html label=cotton/icons/plane.html
<c-vars stroke_width="30" />

<svg {{ attrs }} viewBox="0 0 512 512">
  <g fill="none" stroke="currentColor" stroke-width="{{ stroke_width }}" stroke-linejoin="round">
    <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
    <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
    <path d="M143.533 256 497 127.467l-241 241z"/>
  </g>
</svg>
```

```html label=view.html preview=demo.icons.planes
<c-icons.plane class="size-20 text-red-500" />
<c-icons.plane class="size-20 text-teal-500" />
<c-icons.plane class="size-20 text-gray-500 animate-bounce" />
<c-icons.plane class="size-24 text-purple-500" stroke_width="10" />
```

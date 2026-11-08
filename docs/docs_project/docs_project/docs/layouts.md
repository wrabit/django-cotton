# Composing Layouts

## Building a base layout {#layouts}

Cotton makes building layouts a piece of cake. Let's start with composing a base layout that contains the base of our view:

```html label=cotton/layouts/base.html
<html>
    <head>
        ...
    </head>
    <body>
        {{ slot }}
    </body>
</html>
```

## Create layout variants {#variants}

Imagine that we're creating a web app with an authenticated area, so we'll need areas for guests and users. Let's create these, extending from the base component.

```html label=cotton/layouts/guest.html
<c-layouts.base>
    {{ slot }}
</c-layouts.base>
```

```html label=cotton/layouts/app.html
<c-layouts.base>
    <div class="sidebar">
        {{ sidebar }}
    </div>

    <div class="main">
        {{ slot }}
    </div>
</c-layouts.base>
```

## Using the layouts {#usage}

```html label=login.html
<c-layouts.guest>
    <div id="loginForm">
        <input name="email" type="email" placeholder="Email">
        ...
    </div>
</c-layouts.guest>
```

```html label=dashboard.html
<c-layouts.app>
    <c-slot name="sidebar">
        <a href="/dashboard">Dashboard</a>
        ...
    </c-slot>
    <div id="dashboard">
        ...
    </div>
</c-layouts.app>
```

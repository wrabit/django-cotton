# Reusable Tabs with Alpine.js

## Introduction {#tabs}

> Be sure to check out the notes on Alpine's `:` shorthand under [Attributes](attributes.md#alpine).

Let's tackle together a common UI requirement: tabs.

## Goals {#goals}

We'll start by defining some goals:

- A tab component should be re-usable
- The usage should be simple, keeping markup to a minimum
- It should be able to contain any number of tabs
- It should indicate the active tab

## Start with a static prototype {#prototype}

Before we think about components and adding interactivity, we'll create the design in HTML and Tailwind CSS. This way we can make sure we're happy with the overall look and design.

```html label="Static example" preview=demo.alpine.prototype
<div class="bg-white rounded-lg overflow-hidden border shadow">

    <!-- the navigation for the tabs -->
    <div class="flex items-center space-x-5 w-full bg-gray-100">
        <div class="px-5 py-3 cursor-pointer bg-white text-teal-500">
            Tab 1
        </div>
        <div class="px-5 py-3 cursor-pointer border-b-[3px] border-b-transparent">
            Tab 2
        </div>
    </div>

    <!-- tab's content will go here -->
    <div class="px-5 py-2">
        <p>Lorem ipsum ...</p>
    </div>
</div>
```

## Preparing cotton components {#preparation}

Now we have the design right, let's chop it up into components.

### `<c-tabs />` component

```html label=cotton/tabs.html
<div class="bg-white rounded-lg overflow-hidden border shadow">
    <div class="flex items-center space-x-5 w-full bg-gray-100">
        <!-- tab navigation will go here -->
    </div>

    <div class="px-5 py-2">
        <!-- tab content will go here -->
        {{ slot }}
    </div>
</div>
```

### `<c-tab />` component

```html label=cotton/tab.html
<div>
    {{ slot }}
</div>
```

This will give us the ability to initiate a set of tabs using markup like:

```html label=view.html
<c-tabs>
    <c-tab>Content for tab 1</c-tab>
    <c-tab>Content for tab 2</c-tab>
    <c-tab>Content for tab 3</c-tab>
</c-tabs>
```

## Adding interactivity {#interactivity}

Up to this point, we still don't have a working tabs component. We'll join up the dots now and pull in alpine.js, a lightweight javascript library designed to assist in front end interactions. Follow the [installation guide](https://alpinejs.dev/essentials/installation) before continuing.

## Add an Alpine data component {#data-component}

In alpine you can define re-usable data functions. Place this code somewhere globally in your project.

```xml
<!-- Place this in somewhere like base layout of your app -->
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('tabs', () => ({
            tabs: [],
            currentTab: null,
            isCurrent(tab) {
                return this.currentTab === tab
            },
            register(name) {
                this.tabs.push(name)
            }
        }))
    })
</script>
```

## Modifying tabs.html {#modify-tabs}

Next we'll make the appropriate changes to our tabs.html component to integrate alpine.js

```html label=cotton/tabs.html
<div x-data="tabs" x-init="$watch('tabs', () => currentTab = tabs[0])" class="...">
    <!-- The $watch function will set the first tab as the active tab. -->
    <div class="...">
        <template x-for="tab in tabs">
            <div @click="currentTab = tab" x-text="tab" class="..." :class="currentTab === tab ? 'text-teal-600 font-semibold bg-white' : 'text-gray-500'"></div>
            <!-- Here, we dynamically create the tab navigation items based on the child 'tabs' that are registered. -->
        </template>
    </div>

    <div class="px-5 py-2">
        {{ slot }}
        <!-- All of the <c-tab /> items will go here. -->
    </div>
</div>
```

## Modifying tab.html {#modify-tab}

We now need to modify the tab component so that it is registered each time it is imported into the dom.

```html label=cotton/tab.html
<div x-data x-show="isCurrent('{{ name }}')" x-init="register('{{ name }}')">
    {{ slot }}
</div>
```

## Usage and example {#example}

We have now built a re-usable tab component that satisfies all of our initial goals.

```html label=view.html preview=demo.alpine.tabs
<c-tabs>
    <c-tab name="Tab 1">Tab 1 content</c-tab>
    <c-tab name="Tab 2">Tab 2 content</c-tab>
    <c-tab name="Tab 3">Tab 3 content</c-tab>
</c-tabs>
```

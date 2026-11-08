# HTMX Integration

Cotton helps you build re-usable HTMX-powered components. Define your styles and markup once, then pass different HTMX attributes via `{{ attrs }}`:

```html tab=view.html
<c-button hx-post="/follow" hx-swap="outerHTML">Follow</c-button>

<c-button hx-delete="/posts/1" hx-confirm="Delete?">Delete</c-button>

<c-button hx-get="/load-more" hx-target="#results">Load More</c-button>
```
```html tab=cotton/button.html
<button {{ attrs }} class="btn btn-primary">
    {{ slot }}
</button>
```

### Returning Components from Views

For HTMX partial responses, use `render_component()` to render components directly from your views:

- Create a Cotton component in `cotton/component_name.html`
- Use it in templates: `<c-component-name />`
- Return it from views: `render_component(request, "component-name", context)`
- HTMX swaps it into the DOM seamlessly

> No need for template partials or other libraries. Cotton components work directly as HTMX partials.

## 1. Inline Editing & Delete {#inline-editing}

Common CRUD patterns: edit tasks in-place and delete with confirmation. Try clicking "Edit" or "Delete":

```html tab=view.html preview=demo.htmx.tasks
{% for task in tasks %}
    <c-task :id="task.id" :title="task.title" :description="task.description" />
{% endfor %}
```
```html tab=cotton/task.html
<div id="task-{{ id }}">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <button
        hx-get="/tasks/{{ id }}/edit"
        hx-target="#task-{{ id }}"
        hx-swap="outerHTML"
    >
        Edit
    </button>
    <button
        hx-delete="/tasks/{{ id }}/delete"
        hx-target="#task-{{ id }}"
        hx-swap="delete"
        hx-confirm="Delete this task?"
    >
        Delete
    </button>
</div>
```
```html tab=cotton/task_edit.html
<form
    hx-post="/tasks/{{ id }}/update"
    hx-target="#task-{{ id }}"
    hx-swap="outerHTML"
>
    {% csrf_token %}
    <input type="text" name="title" value="{{ title }}">
    <textarea name="description">{{ description }}</textarea>
    <button type="submit">Save</button>
    <button
        type="button"
        hx-get="/tasks/{{ id }}"
        hx-target="#task-{{ id }}"
        hx-swap="outerHTML"
    >
        Cancel
    </button>
</form>
```
```python tab=views.py
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_cotton import render_component
from .models import Task

def task_detail(request, id):
    task = get_object_or_404(Task, id=id)
    return HttpResponse(
        render_component(request, "task-display",
            id=task.id,
            title=task.title,
            description=task.description,
        )
    )

def task_edit(request, id):
    task = get_object_or_404(Task, id=id)
    return HttpResponse(
        render_component(request, "task-edit",
            id=task.id,
            title=task.title,
            description=task.description,
        )
    )

def task_update(request, id):
    task = get_object_or_404(Task, id=id)
    task.title = request.POST.get('title')
    task.description = request.POST.get('description')
    task.save()
    return HttpResponse(
        render_component(request, "task-display",
            id=task.id,
            title=task.title,
            description=task.description,
        )
    )

def task_delete(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    return HttpResponse('')
```

## 2. Form Validation {#form-validation}

Validate fields inline on blur without a full page reload:

```html tab=view.html preview=demo.htmx.validation
<c-email-field
    hx-post="/validate-email"
    hx-trigger="blur from:find input"
    hx-target="this"
    hx-swap="outerHTML"
/>
```
```html tab=email_field.html
<div {{ attrs }}>
    <label for="email">Email</label>
    <input type="email" id="email" name="email" value="{{ value }}">
    {% if error %}<p>{{ error }}</p>{% endif %}
</div>
```
```python tab=views.py
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django_cotton import render_component

def validate_email_field(request):
    value = request.POST.get('email', '')
    error = None

    if value:
        try:
            validate_email(value)
        except ValidationError:
            error = 'Invalid email address'

    return HttpResponse(
        render_component(request, "email-field", value=value, error=error)
    )
```

## 3. Modal Loading with Alpine.js {#modal-loading}

Combine Cotton, HTMX, and Alpine.js to load dynamic content into modals. Click "View Details" on any user:

```html tab=view.html preview=demo.htmx.modal-users
<c-modal />

{% for user in users %}
    <div>
        <span>{{ user.name }}</span>
        <button
            hx-get="/users/{{ user.id }}/details"
            hx-target="#modal-content"
            @click="$dispatch('open-modal')"
        >
            View Details
        </button>
    </div>
{% endfor %}
```
```html tab=modal.html
<div x-data="{ open: false }"
     x-on:open-modal.window="open = true"
     x-on:close-modal.window="open = false">
    <div x-show="open" @click="open = false"></div>
    <div x-show="open">
        <div id="modal-content">{{ slot }}</div>
    </div>
</div>
```
```html tab=user_details.html
<div>
    <h2>{{ name }}</h2>
    <p>Email: {{ email }}</p>
    <button @click="$dispatch('close-modal')">Close</button>
</div>
```
```python tab=views.py
from django.http import HttpResponse
from django_cotton import render_component

def user_details(request, id):
    user = get_object_or_404(User, id=id)
    return HttpResponse(
        render_component(request, "user-details",
            name=user.get_full_name(),
            email=user.email,
        )
    )
```

## 4. Search with Debounce {#search-debounce}

Live search results with debouncing (`delay:500ms`) to avoid excessive requests. Try searching:

```html tab=view.html preview=demo.htmx.search
<input
    type="search"
    name="q"
    placeholder="Search..."
    hx-get="/search"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#search-results"
    hx-include="this"
>

<c-search-results />
```
```html tab=search_results.html
<div id="search-results">
    {% if results %}
        {% for result in results %}
            <div>
                <h4>{{ result.title }}</h4>
                <p>{{ result.description }}</p>
            </div>
        {% endfor %}
    {% elif query %}
        <p>No results for "{{ query }}"</p>
    {% else %}
        <p>Start typing to search...</p>
    {% endif %}
</div>
```
```python tab=views.py
from django.http import HttpResponse
from django_cotton import render_component

def search(request):
    query = request.GET.get('q', '')
    results = Article.objects.filter(title__icontains=query)[:10] if query else []

    return HttpResponse(
        render_component(request, "search-results",
            results=results,
            query=query,
        )
    )
```

### Key Takeaways

- Use `{{ attrs }}` to pass HTMX attributes to styled components
- Use `render_component()` to return Cotton components as HTMX partial responses
- No need for template partials or special configuration
- Components maintain their reusability while serving dynamic content
- Combine with Alpine.js for enhanced interactivity

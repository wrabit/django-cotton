from __future__ import annotations

from typing import Optional

from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse


class CottonStackMiddleware:
    """Post-process rendered templates to resolve cotton push/stack placeholders."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Flag the request so template tags know middleware is active.
        setattr(request, "_cotton_stack_middleware", True)
        response = self.get_response(request)
        return self._process_response(request, response)

    def _process_response(self, request, response: HttpResponse):
        if isinstance(response, SimpleTemplateResponse) and not response.is_rendered:
            response.render()

        return self._apply(response, request)

    def _apply(self, response: HttpResponse, request) -> HttpResponse:
        cotton_state = getattr(request, "_cotton_stack_state", None)

        if not cotton_state:
            return response

        placeholders = cotton_state.get("stack_placeholders") or []
        push_stacks = cotton_state.get("push_stacks") or {}

        if not placeholders:
            self._reset(cotton_state, request)
            return response

        if getattr(response, "streaming", False):
            self._reset(cotton_state, request)
            return response

        content_type = response.get("Content-Type", "")
        if "html" not in content_type and "xml" not in content_type:
            self._reset(cotton_state, request)
            return response

        rendered = self._get_response_content(response)
        if rendered is None:
            self._reset(cotton_state, request)
            return response

        for placeholder in placeholders:
            stack_name = placeholder["name"]
            stack = push_stacks.get(stack_name, {})
            items = stack.get("items", [])
            replacement = "".join(items) if items else placeholder.get("fallback", "")
            rendered = rendered.replace(placeholder["placeholder"], replacement, 1)

        response.content = rendered

        self._reset(cotton_state, request)

        return response

    @staticmethod
    def _get_response_content(response: HttpResponse) -> Optional[str]:
        if isinstance(response, SimpleTemplateResponse):
            # SimpleTemplateResponse keeps rendered content accessible via property.
            if response.is_rendered:
                return response.rendered_content
        content = response.content
        if content is None:
            return None
        if isinstance(content, bytes):
            charset = getattr(response, "charset", "utf-8") or "utf-8"
            return content.decode(charset, errors="ignore")
        return str(content)

    @staticmethod
    def _reset(cotton_state: dict, request) -> None:
        push_stacks = cotton_state.get("push_stacks")
        if isinstance(push_stacks, dict):
            push_stacks.clear()

        placeholders = cotton_state.get("stack_placeholders")
        if isinstance(placeholders, list):
            placeholders.clear()

        if hasattr(request, "_cotton_stack_state"):
            delattr(request, "_cotton_stack_state")

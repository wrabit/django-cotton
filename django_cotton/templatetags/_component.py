from typing import Dict, Any
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.template import Node, Template, Variable, VariableDoesNotExist
from django.template.base import Token, Parser
import ast

from django_cotton.utils import ensure_quoted


class CottonIncompleteDynamicComponentError(Exception):
    """Raised when a dynamic component is missing required attributes."""


def cotton_component(parser: Parser, token: Token) -> "CottonComponentNode":
    """
    Template tag to render a cotton component with dynamic attributes.
    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise ValueError("cotton_component tag requires at least a component path and key.")

    component_path = bits[1]
    component_key = bits[2]

    kwargs = {}
    for bit in bits[3:]:
        if "=" in bit:
            key, value = bit.split("=", 1)
        else:
            key, value = bit, ""
        kwargs[key] = value

    nodelist = parser.parse(("end_cotton_component",))
    parser.delete_first_token()

    return CottonComponentNode(nodelist, component_path, component_key, kwargs)


class CottonComponentNode(Node):
    def __init__(self, nodelist, component_path: str, component_key: str, kwargs: Dict[str, str]):
        self.nodelist = nodelist
        self.component_path = component_path
        self.component_key = component_key
        self.kwargs = kwargs

    def render(self, context) -> str:
        slot = self.nodelist.render(context)
        attrs = self._build_attrs(context)

        named_slots_ctx = self._process_named_slots(context)
        self._evaluate_expression_attributes(attrs, named_slots_ctx, context)

        template = self._get_template(context, attrs)
        attrs_string = self._build_attrs_string(attrs)
        accessible_attrs = {key.replace("-", "_"): value for key, value in attrs.items()}

        return self._render_template(
            template, context, slot, attrs, attrs_string, accessible_attrs, named_slots_ctx
        )

    def _build_attrs(self, context) -> Dict[str, Any]:
        attrs = {}
        for key, value in self.kwargs.items():
            value = self._strip_quotes(value)
            if key.startswith(":"):
                key = key[1:]
                attrs[key] = self._process_dynamic_attribute(key, value, context)
            elif value == "":
                attrs[key] = True
            else:
                attrs[key] = value
        return attrs

    @staticmethod
    def _strip_quotes(value: str) -> str:
        if value and value[0] == value[-1] and value[0] in ('"', "'"):
            return value[1:-1]
        return value

    def _process_dynamic_attribute(self, key: str, value: str, context) -> Any:
        try:
            return Variable(value).resolve(context)
        except VariableDoesNotExist:
            pass

        if value == "":
            return True

        value = self._parse_template_string(value, context)

        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass

        context.setdefault("ctn_unprocessable_dynamic_attrs", set()).add(key)
        return ""

    def _process_named_slots(self, context) -> Dict[str, Any]:
        all_named_slots_ctx = context.get("cotton_named_slots", {})
        named_slots_ctx = all_named_slots_ctx.get(self.component_key, {})
        all_named_slots_ctx[self.component_key] = {}
        return named_slots_ctx

    def _evaluate_expression_attributes(
        self, attrs: Dict[str, Any], named_slots_ctx: Dict[str, Any], context
    ) -> None:
        if "ctn_template_expression_attrs" in named_slots_ctx:
            for key in named_slots_ctx["ctn_template_expression_attrs"]:
                if key.startswith(":"):
                    evaluated = self._process_dynamic_attribute(key, named_slots_ctx[key], context)
                    key = key[1:]
                    attrs[key] = evaluated
                else:
                    attrs[key] = named_slots_ctx[key]

    def _get_template(self, context, attrs: Dict[str, Any]) -> Template:
        template_path = self._generate_component_template_path(attrs)
        cache = context.render_context.get(self)
        if cache is None:
            cache = context.render_context[self] = {}

        template = cache.get(template_path)
        if template is None:
            template = get_template(template_path)
            if hasattr(template, "template"):
                template = template.template
            cache[template_path] = template

        return template

    def _generate_component_template_path(self, attrs: Dict[str, Any]) -> str:
        if self.component_path == "component":
            if "is" not in attrs:
                raise CottonIncompleteDynamicComponentError(
                    'Cotton error: "<c-component>" should be accompanied by an "is" attribute.'
                )
            component_path = attrs["is"]
        else:
            component_path = self.component_path

        component_tpl_path = component_path.replace(".", "/").replace("-", "_")
        cotton_dir = getattr(settings, "COTTON_DIR", "cotton")
        return f"{cotton_dir}/{component_tpl_path}.html"

    @staticmethod
    def _build_attrs_string(attrs: Dict[str, Any]) -> str:
        return " ".join(f"{key}={ensure_quoted(value)}" for key, value in attrs.items())

    def _render_template(
        self,
        template: Template,
        context,
        slot: str,
        attrs: Dict[str, Any],
        attrs_string: str,
        accessible_attrs: Dict[str, Any],
        named_slots_ctx: Dict[str, Any],
    ) -> str:
        with context.push(
            {
                "slot": slot,
                "attrs_dict": attrs,
                "attrs": mark_safe(attrs_string),
                **accessible_attrs,
                **named_slots_ctx,
            }
        ):
            return template.render(context)

    @staticmethod
    def _parse_template_string(value: str, context) -> str:
        try:
            return Template(value).render(context)
        except (ValueError, SyntaxError):
            return value

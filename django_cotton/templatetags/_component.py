import functools
from typing import Union

from django.conf import settings
from django.template import Library
from django.template.base import (
    Variable,
    VariableDoesNotExist,
    Node,
)
from django.template.context import ContextDict, Context
from django.template.loader import get_template

from django_cotton.utils import get_cotton_data
from django_cotton.exceptions import CottonIncompleteDynamicComponentError
from django_cotton.templatetags import Attrs, DynamicAttr, UnprocessableDynamicAttr

register = Library()


class CottonComponentNode(Node):
    def __init__(self, component_name, nodelist, attrs):
        self.component_name = component_name
        self.nodelist = nodelist
        self.attrs = attrs
        self.template_cache = {}

    def render(self, context):
        cotton_data = get_cotton_data(context)

        # Push a new component onto the stack
        component_data = {
            "key": self.component_name,
            "attrs": Attrs({}),
            "slots": {},
        }
        cotton_data["stack"].append(component_data)

        # Process simple attributes and boolean attributes
        for key, value in self.attrs.items():
            value = self._strip_quotes_safely(value)
            if value is True:  # Boolean attribute
                component_data["attrs"][key] = True
            elif key.startswith(":"):
                key = key[1:]
                try:
                    component_data["attrs"][key] = DynamicAttr(value).resolve(context)
                except UnprocessableDynamicAttr:
                    component_data["attrs"].unprocessable(key)
            else:
                component_data["attrs"][key] = value

        # Render the nodelist to process any slot tags and vars
        default_slot = self.nodelist.render(context)

        # Prepare the cotton-specific data
        component_state = {
            **component_data["slots"],
            **component_data["attrs"].make_attrs_accessible(),
            "attrs": component_data["attrs"],
            "slot": default_slot,
            "cotton_data": cotton_data,
        }

        template = self._get_cached_template(context, component_data["attrs"])
        # excludes builtin + custom context processors
        # output = template.render(context.new(component_state))

        # provides global
        with context.push(component_state):
            output = template.render(context)

        cotton_data["stack"].pop()

        return output

    def _get_cached_template(self, context, attrs):
        cache = context.render_context.get(self)
        if cache is None:
            cache = context.render_context[self] = {}

        template_path = self._generate_component_template_path(self.component_name, attrs.get("is"))

        if template_path not in cache:
            template = get_template(template_path)
            if hasattr(template, "template"):
                template = template.template
            cache[template_path] = template

        return cache[template_path]

    @staticmethod
    @functools.lru_cache(maxsize=400)
    def _generate_component_template_path(component_name: str, is_: Union[str, None]) -> str:
        """Generate the path to the template for the given component name."""
        if component_name == "component":
            if is_ is None:
                raise CottonIncompleteDynamicComponentError(
                    'Cotton error: "<c-component>" should be accompanied by an "is" attribute.'
                )
            component_name = is_

        component_tpl_path = component_name.replace(".", "/").replace("-", "_")
        cotton_dir = getattr(settings, "COTTON_DIR", "cotton")
        return f"{cotton_dir}/{component_tpl_path}.html"

    @staticmethod
    def _strip_quotes_safely(value):
        if type(value) is str and value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value


def cotton_component(parser, token):
    bits = token.split_contents()[1:]
    component_name = bits[0]
    attrs = {}
    for bit in bits[1:]:
        try:
            key, value = bit.split("=")
            attrs[key] = value
        except ValueError:
            attrs[bit] = True

    nodelist = parser.parse(("endc",))
    parser.delete_first_token()

    return CottonComponentNode(component_name, nodelist, attrs)

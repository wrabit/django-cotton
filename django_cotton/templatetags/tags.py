import functools
from typing import Union, List

from django.conf import settings
from django.template import Library
from django.template.base import (
    Variable,
    VariableDoesNotExist,
    Node,
    TemplateSyntaxError,
)
from django.template.loader import get_template
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from django_cotton.exceptions import CottonIncompleteDynamicComponentError
from django_cotton.templatetags._context_models import Attrs, DynamicAttr, UnprocessableDynamicAttr
from django_cotton.utils import get_cotton_data

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
                try:
                    component_data["attrs"][key] = Variable(value).resolve(context)
                except (VariableDoesNotExist, IndexError):
                    component_data["attrs"][key] = value

        # Render the nodelist to process any slot tags and vars
        default_slot = self.nodelist.render(context)

        # Prepare the cotton-specific data
        component_state = {
            "attrs": component_data["attrs"],
            "slot": default_slot,
            **component_data["slots"],
            **component_data["attrs"].make_attrs_accessible(),
        }

        template = self._get_cached_template(context, component_data["attrs"])

        # Render the template with the new context
        with context.push(**component_state):
            output = template.render(context)

        # Pop the component from the stack
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


@register.tag("comp")
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

    nodelist = parser.parse(("endcomp",))
    parser.delete_first_token()

    return CottonComponentNode(component_name, nodelist, attrs)


@register.tag("slot")
def cotton_slot(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) < 1:
        raise TemplateSyntaxError("cotton slot tag must include a 'name'")

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()
    return CottonSlotNode(bits[0], nodelist)


class CottonSlotNode(Node):
    def __init__(self, slot_name, nodelist):
        self.slot_name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            content = self.nodelist.render(context)
            cotton_data["stack"][-1]["slots"][self.slot_name] = mark_safe(content)
        else:
            raise TemplateSyntaxError("<slot /> tag must be used inside a component")
        return ""


@register.tag("complexattr")
def cotton_slot(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) < 1:
        raise TemplateSyntaxError("cotton complex-attr must include a 'name'")

    nodelist = parser.parse(("endcomplexattr",))
    parser.delete_first_token()
    return ComplexAttrNode(bits[0], nodelist)


class ComplexAttrNode(Node):
    def __init__(self, attr_name, nodelist):
        self.attr_name = attr_name
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            content = self.nodelist.render(context)
            if self.attr_name.startswith(":"):
                key = self.attr_name[1:]
                try:
                    cotton_data["stack"][-1]["attrs"][key] = DynamicAttr(content).resolve(context)
                except UnprocessableDynamicAttr:
                    cotton_data["stack"][-1]["attrs"].unprocessable(key)
            else:
                # just template partial
                cotton_data["stack"][-1]["attrs"][self.attr_name] = mark_safe(content)
        return ""


class CottonVarsNode(Node):
    def __init__(self, var_dict, empty_vars: List, nodelist):
        self.var_dict = var_dict
        self.empty_vars = empty_vars
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)

        if cotton_data["stack"]:
            current_component = cotton_data["stack"][-1]
            attrs = current_component["attrs"]

            # Process and resolve the merged vars
            for key, value in self.var_dict.items():
                attrs.exclude_from_string_output(key)
                if key not in attrs.exclude_unprocessable():
                    if key.startswith(":"):
                        try:
                            attrs[key[1:]] = DynamicAttr(value, is_cvar=True).resolve(context)
                        except UnprocessableDynamicAttr:
                            pass
                    else:
                        try:
                            resolved_value = Variable(value).resolve(context)
                        except VariableDoesNotExist:
                            resolved_value = value
                        attrs[key] = resolved_value

            # print(attrs.dict)

            # Process cvars without values
            for empty_var in self.empty_vars:
                attrs.exclude_from_string_output(empty_var)

            with context.push({**attrs.make_attrs_accessible(), "attrs": attrs}):
                output = self.nodelist.render(context)

            return output

        else:
            raise TemplateSyntaxError("<c-vars /> tag must be used inside a component")


@register.tag("cvars")
def cotton_vars(parser, token):
    bits = token.split_contents()[1:]
    var_dict = {}
    empty_vars = []
    for bit in bits:
        try:
            key, value = bit.split("=")
            var_dict[key] = value.strip("\"'")
        except ValueError:
            empty_vars.append(bit)

    nodelist = parser.parse(("endcvars",))
    parser.delete_first_token()

    return CottonVarsNode(var_dict, empty_vars, nodelist)


@register.filter
def merge(attrs, args):
    # attrs is expected to be a dictionary of existing attributes
    # args is a string of additional attributes to merge, e.g., "class:extra-class"
    for arg in args.split(","):
        key, value = arg.split(":", 1)
        if key in attrs:
            attrs[key] = value + " " + attrs[key]
        else:
            attrs[key] = value
    return format_html_join(" ", '{0}="{1}"', attrs.items())


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

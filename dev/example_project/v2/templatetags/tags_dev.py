import ast
from collections.abc import Mapping
from typing import Union, Set

from django.conf import settings
from django.template import Library
from django.template.base import (
    Variable,
    VariableDoesNotExist,
    Node,
    TemplateSyntaxError,
    Template,
)
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = Library()


class CottonIncompleteDynamicComponentErrorV2(Exception):
    """Raised when a dynamic component is missing required attributes."""


class DynamicAttr:
    def __init__(self, value: str):
        self.value = value
        self._resolved_value = None
        self._unprocessable = False

    @property
    def is_unprocessable(self):
        return self._unprocessable

    def resolve(self, context):
        if self._resolved_value is not None:
            return self._resolved_value

        try:
            self._resolved_value = Variable(self.value).resolve(context)
            return self._resolved_value
        except VariableDoesNotExist:
            pass

        if self.value == "":
            self._resolved_value = True
            return self._resolved_value

        try:
            template = Template(
                f"{{% with True as True and False as False and None as None %}}{self.value}{{% endwith %}}"
            )
            rendered_value = template.render(context)
            if rendered_value != self.value:
                self._resolved_value = rendered_value
                return self._resolved_value
        except TemplateSyntaxError:
            pass

        try:
            self._resolved_value = ast.literal_eval(self.value)
            return self._resolved_value
        except (ValueError, SyntaxError):
            pass

        self._unprocessable = True
        self._resolved_value = self.value
        return self._resolved_value


class Attrs(Mapping):
    def __init__(self, attrs):
        self._attrs = attrs
        self._exclude_from_str: Set[str] = set()

    def __str__(self):
        return " ".join(
            f'{k}="{v}"'
            for k, v in self._attrs.items()
            if k not in self._exclude_from_str
        )

    def __getitem__(self, key):
        return self._attrs[key]

    def __iter__(self):
        return iter(self._attrs)

    def __len__(self):
        return len(self._attrs)

    def __contains__(self, key):
        return key in self._attrs

    def get(self, key, default=None):
        return self._attrs.get(key, default)

    def items(self):
        return self._attrs.items()

    def keys(self):
        return self._attrs.keys()

    def values(self):
        return self._attrs.values()

    @property
    def dict(self):
        return self._attrs

    # Custom methods to allow modifications
    def update(self, other):
        self._attrs.update(other)

    def __setitem__(self, key, value):
        self._attrs[key] = value

    def pop(self, key, default=None):
        return self._attrs.pop(key, default)

    def exclude(self, key):
        self._exclude_from_str.add(key)


class UnprocessableValue:
    def __init__(self, original_value):
        self.original_value = original_value


class CottonComponentNode(Node):
    def __init__(self, component_name, nodelist, attrs):
        self.component_name = component_name
        self.nodelist = nodelist
        self.attrs = attrs

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
                component_data["attrs"][key[1:]] = DynamicAttr(value).resolve(context)
            else:
                try:
                    component_data["attrs"][key] = Variable(value).resolve(context)
                except VariableDoesNotExist:
                    component_data["attrs"][key] = value

        # Render the nodelist to process any slot tags and vars
        default_slot = self.nodelist.render(context)

        # Process dynamic attributes from named slots
        for slot_name, slot_content in component_data["slots"].items():
            if slot_name.startswith(":"):
                # attr_name = slot_name[1:]  # Remove the ':' prefix
                # resolved_value = self._process_dynamic_value(slot_content, context)
                # component_data["attrs"][attr_name] = resolved_value
                if isinstance(slot_content, DynamicAttr):
                    component_data["attrs"][slot_name[1:]] = slot_content.resolve(
                        context
                    )
                else:
                    component_data["attrs"][slot_name[1:]] = slot_content

        # Prepare the cotton-specific data
        cotton_specific = {
            "attrs": component_data["attrs"],
            "slot": default_slot,
            **component_data["slots"],
            **component_data["attrs"],
        }

        # template_name = f"{self.component_name.replace('-', '_')}.html"
        template_name = self._generate_component_template_path(
            self.component_name, component_data["attrs"].get("is")
        )

        # Use the base.Template of a backends.django.Template.
        template = get_template(template_name)
        if hasattr(template, "template"):
            template = template.template

        # Render the template with the new context
        with context.push(**cotton_specific):
            output = template.render(context)

        # Pop the component from the stack
        cotton_data["stack"].pop()

        return output

    def _process_dynamic_value(self, value, context):
        """Process a dynamic value, attempting to resolve it as a variable, template string, or literal."""
        try:
            # Try to resolve as a variable
            return Variable(value).resolve(context)
        except VariableDoesNotExist:
            try:
                # Try to parse as a template string
                template = Template(
                    f"{{% with True as True and False as False and None as None %}}{value}{{% endwith %}}"
                )
                rendered_value = template.render(context)

                # Check if the rendered value is different from the original
                if rendered_value != value:
                    return rendered_value
                else:
                    # If it's the same, move on to the next step
                    raise ValueError("Template rendering did not change the value")
            except (TemplateSyntaxError, ValueError):
                try:
                    # Try to parse as an AST literal
                    return ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    # Flag as unprocessable if none of the above worked
                    return UnprocessableValue(value)

    def _generate_component_template_path(
        self, component_name: str, is_: Union[str, None]
    ) -> str:
        """Generate the path to the template for the given component name."""
        if component_name == "component":
            if is_ is None:
                raise CottonIncompleteDynamicComponentErrorV2(
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


def get_cotton_data(context):
    if "cotton_data" not in context:
        context["cotton_data"] = {"stack": [], "vars": {}}
    return context["cotton_data"]


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
    slot_name = bits[0]
    is_expression = "expression" in bits[1:] if len(bits) > 1 else False

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()
    return CottonSlotNode(slot_name, nodelist, is_expression)


class CottonSlotNode(Node):
    def __init__(self, slot_name, nodelist, is_expression):
        self.slot_name = slot_name
        self.nodelist = nodelist
        self.is_expression = is_expression

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            content = self.nodelist.render(context)
            if self.is_expression:
                cotton_data["stack"][-1]["slots"][self.slot_name] = DynamicAttr(content)
            else:
                cotton_data["stack"][-1]["slots"][self.slot_name] = mark_safe(content)
        return ""


class CottonVarsNode(Node):
    def __init__(self, var_dict, nodelist):
        self.var_dict = var_dict
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            current_component = cotton_data["stack"][-1]
            attrs = current_component["attrs"]

            # Process and resolve the merged vars
            for key, value in self.var_dict.items():
                if key not in attrs:
                    try:
                        resolved_value = Variable(value).resolve(context)
                    except VariableDoesNotExist:
                        resolved_value = value
                    attrs[key] = resolved_value
                attrs.exclude(key)

            # Render the wrapped content with the new context
            with context.push({**attrs, "attrs": attrs}):
                return self.nodelist.render(context)

        return ""


@register.tag("cvars")
def cotton_vars(parser, token):
    bits = token.split_contents()[1:]
    var_dict = {}
    for bit in bits:
        try:
            key, value = bit.split("=")
            var_dict[key] = value.strip("\"'")
        except ValueError:
            var_dict[bit] = "True"

    nodelist = parser.parse(("endcvars",))
    parser.delete_first_token()

    return CottonVarsNode(var_dict, nodelist)

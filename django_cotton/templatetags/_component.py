import ast

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.template import Node, Template, Context

from django_cotton.utils import ensure_quoted


class CottonIncompleteDynamicComponentException(Exception):
    pass


def cotton_component(parser, token):
    """
    Template tag to render a cotton component with dynamic attributes.

    Expected structure: {% cotton_component 'component_path' 'component_key' key1="value1" :key2="dynamic_value" %}
    """
    bits = token.split_contents()
    component_path = bits[1]
    component_key = bits[2]

    kwargs = {}
    for bit in bits[3:]:
        try:
            key, value = bit.split("=")
        except ValueError:
            # No value provided, assume boolean attribute
            key = bit
            value = ""

        kwargs[key] = value

    nodelist = parser.parse(("end_cotton_component",))
    parser.delete_first_token()

    return CottonComponentNode(nodelist, component_path, component_key, kwargs)


class CottonComponentNode(Node):
    def __init__(self, nodelist, component_path, component_key, kwargs):
        self.nodelist = nodelist
        self.component_path = component_path
        self.component_key = component_key
        self.kwargs = kwargs

    def render(self, context):
        attrs = self._build_attrs(context)

        # Add the remainder as the default slot
        ctx = context.flatten()
        ctx["slot"] = self.nodelist.render(context)

        # Merge slots and attributes into the local context
        all_named_slots_ctx = context.get("cotton_named_slots", {})
        named_slots_ctx = all_named_slots_ctx.get(self.component_key, {})
        ctx.update(named_slots_ctx)

        # We need to check if any dynamic attributes are present in the component slots, process them and move them over to attrs
        if "ctn_template_expression_attrs" in named_slots_ctx:
            for expression_attr in named_slots_ctx["ctn_template_expression_attrs"]:
                # Process them like a non-extracted attribute
                if expression_attr[0] == ":":
                    evaluated = self._process_dynamic_attribute(
                        named_slots_ctx[expression_attr], ctx
                    )
                    expression_attr = expression_attr[1:]
                    attrs[expression_attr] = evaluated
                else:
                    attrs[expression_attr] = named_slots_ctx[expression_attr]

        attrs_string = " ".join(f"{key}={ensure_quoted(value)}" for key, value in attrs.items())
        ctx["attrs"] = mark_safe(attrs_string)
        ctx["attrs_dict"] = attrs

        # Ensure attributes are accessible, eg. 'x-init' -> {{ x_init }}
        attrs = {key.replace("-", "_"): value for key, value in attrs.items()}
        ctx.update(attrs)

        # Reset the component's slots in context to prevent data leaking between components.
        all_named_slots_ctx[self.component_key] = {}

        template_path = self._generate_component_template_path(attrs)

        return get_template(template_path).render(ctx)

    def _build_attrs(self, context):
        """
        Build the attributes dictionary for the component
        """
        attrs = {}

        for key, value in self.kwargs.items():
            # strip single or double quotes only if both sides have them
            if value and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            if key.startswith(":"):
                key = key[1:]
                attrs[key] = self._process_dynamic_attribute(value, context)
            elif value == "":
                attrs[key] = True
            else:
                attrs[key] = value

        return attrs

    def _process_dynamic_attribute(self, value, context):
        """
        Process a dynamic attribute (prefixed with ":")
        """
        # We might be passing a variable by reference
        try:
            value = template.Variable(value).resolve(context)
            return value
        except (template.VariableDoesNotExist, IndexError):
            pass

        # Boolean attribute?
        if value == "":
            return True

        # Could be a string literal but process any template strings first to handle intermingled expressions
        value = self._parse_template_string(value, context)

        # Finally, try to evaluate the value as a Python literal
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def _generate_component_template_path(self, attrs):
        """Check if the component is dynamic else process the path as is"""

        if self.component_path == "component":
            # Dynamic component. 'is' at this point is already processed from kwargs to attrs, so it's already expression attribute,
            # dynamic + template var enabled. Therefore we can do either :is="variable" or is="some.path.{{ variable }}"
            if "is" in attrs:
                component_path = attrs["is"]

            else:
                return CottonIncompleteDynamicComponentException(
                    'Cotton error: "<c-component>" should be accompanied by an "is" attribute.'
                )
        else:
            component_path = self.component_path

        component_tpl_path = component_path.replace(".", "/").replace("-", "_")

        return "{}/{}.html".format(
            settings.COTTON_DIR if hasattr(settings, "COTTON_DIR") else "cotton", component_tpl_path
        )

    def _parse_template_string(self, value, context):
        try:
            return Template(value).render(Context(context))
        except (ValueError, SyntaxError):
            return value

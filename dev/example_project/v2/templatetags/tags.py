import ast

from django.template import (
    Variable,
    VariableDoesNotExist,
    Library,
    Node,
    TemplateSyntaxError,
    Template,
)
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = Library()


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
        cotton_data["stack"].append(
            {
                "key": self.component_name,
                "attrs": {},
                "slots": {},
            }
        )

        # Resolve and add attributes
        resolved_attrs = {}
        for key, value in self.attrs.items():
            if key.startswith(":"):
                original_value = value
                key = key[1:]  # Remove the ':' prefix
                try:
                    # Try to resolve as a variable
                    resolved_value = Variable(value).resolve(context)
                except VariableDoesNotExist:
                    try:
                        # Try to parse as a template string
                        template = Template(
                            f"{{% with True as True and False as False and None as None %}}{value}{{% endwith %}}"
                        )
                        rendered_value = template.render(context)

                        # Check if the rendered value is different from the original
                        if rendered_value != original_value:
                            resolved_value = rendered_value
                        else:
                            # If it's the same, move on to the next step
                            raise ValueError(
                                "Template rendering did not change the value"
                            )
                    except (TemplateSyntaxError, ValueError):
                        try:
                            # Try to parse as an AST literal
                            resolved_value = ast.literal_eval(value)
                        except (ValueError, SyntaxError):
                            # Flag as unprocessable if none of the above worked
                            resolved_value = UnprocessableValue(original_value)

                resolved_attrs[key] = resolved_value
            else:
                resolved_attrs[key] = value

        cotton_data["stack"][-1]["attrs"] = resolved_attrs

        # Resolve and add attributes
        # resolved_attrs = {}
        # for key, value in self.attrs.items():
        #     try:
        #         resolved_attrs[key] = Variable(value).resolve(context)
        #     except VariableDoesNotExist:
        #         resolved_attrs[key] = value

        # cotton_data["stack"][-1]["attrs"] = resolved_attrs

        # Render the nodelist to process any slot tags and vars
        slot_content = self.nodelist.render(context)

        # If there's no explicit default slot, use the entire rendered content
        if "default" not in cotton_data["stack"][-1]["slots"]:
            cotton_data["stack"][-1]["slots"]["default"] = slot_content

        # Prepare attrs string, excluding vars
        attrs_dict = {
            k: v for k, v in resolved_attrs.items() if k not in cotton_data["vars"]
        }
        attrs_string = " ".join(f'{k}="{v}"' for k, v in attrs_dict.items())

        # Prepare the Cotton-specific data
        cotton_specific = {
            "attrs": mark_safe(attrs_string),
            "attrs_dict": attrs_dict,
            "slot": cotton_data["stack"][-1]["slots"].get("default", ""),
            **cotton_data["stack"][-1]["slots"],
            **cotton_data["vars"],
        }

        template_name = f"{self.component_name.replace('-', '_')}.html"

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
            attrs[key] = value.strip("\"'")
        except ValueError:
            attrs[bit] = True

    nodelist = parser.parse(("endcomp",))
    parser.delete_first_token()

    return CottonComponentNode(component_name, nodelist, attrs)


@register.tag("slot")
def cotton_slot(parser, token):
    bits = token.split_contents()[1:]
    attrs = {}
    for bit in bits:
        try:
            key, value = bit.split("=")
            attrs[key] = value.strip("\"'")
        except ValueError:
            attrs[bit] = True

    if "name" not in attrs:
        raise TemplateSyntaxError("slot tag must include a 'name' attribute")

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()
    return CottonSlotNode(attrs["name"], nodelist)


class CottonSlotNode(Node):
    def __init__(self, slot_name, nodelist):
        self.slot_name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if cotton_data["stack"]:
            content = self.nodelist.render(context)
            cotton_data["stack"][-1]["slots"][self.slot_name] = content
        return ""


class CottonVarsNode(Node):
    def __init__(self, var_dict):
        self.var_dict = var_dict

    def render(self, context):
        cotton_data = get_cotton_data(context)
        if len(cotton_data["stack"]) > 1:  # Ensure we're inside a component
            parent_vars = cotton_data["stack"][-2].setdefault("vars", {})
            for key, value in self.var_dict.items():
                try:
                    resolved_value = Variable(value).resolve(context)
                except VariableDoesNotExist:
                    resolved_value = value
                parent_vars[key] = resolved_value
        else:
            # We're not inside a nested component, so we'll add to the current level
            current_vars = cotton_data["stack"][-1].setdefault("vars", {})
            for key, value in self.var_dict.items():
                try:
                    resolved_value = Variable(value).resolve(context)
                except VariableDoesNotExist:
                    resolved_value = value
                current_vars[key] = resolved_value
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

    return CottonVarsNode(var_dict)

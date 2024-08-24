from django import template
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted

register = template.Library()


def cotton_vars_frame(parser, token):
    """The job of the vars frame is:
    1. to filter out attributes declared as vars inside {{ attrs }} string.
    2. to provide default values to attributes.
    Because we're effecting variables inside the same component, which is not possible usually, we we wrap
    the vars frame around the contents of the component so we can govern the attributes and vars that are available.
    """
    bits = token.split_contents()[1:]  # Skip the tag name

    # We dont use token_kwargs because it doesn't allow for hyphens in key names, i.e. x-data=""
    tag_kwargs = {}
    for bit in bits:
        key, value = bit.split("=")
        tag_kwargs[key] = parser.compile_filter(value)

    nodelist = parser.parse(("endcotton_vars_frame",))
    parser.delete_first_token()
    return CottonVarsFrameNode(nodelist, tag_kwargs)


class CottonVarsFrameNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        # Retrieve attrs_dict from parent _component
        provided_attrs = context.get("attrs_dict", {})

        # Initialize vars based on the frame's kwargs and parent attrs
        c_vars = {}
        for key, value in self.kwargs.items():
            # Check if the var exists in component attrs; if so, use it, otherwise use the resolved default
            if key in provided_attrs:
                c_vars[key] = provided_attrs[key]
            else:
                # Attempt to resolve each kwarg value (which may include template variables)
                resolved_value = value.resolve(context)
                c_vars[key] = resolved_value

        # Overwrite 'attrs' in the local context by excluding keys that are identified as vars
        attrs_dict = {k: v for k, v in provided_attrs.items() if k not in c_vars}

        # Provide all of the attrs as a string to pass to the component before any '-' to '_' replacing
        attrs_string = " ".join(f"{k}={ensure_quoted(v)}" for k, v in attrs_dict.items())
        context["attrs"] = mark_safe(attrs_string)
        context["attrs_dict"] = attrs_dict

        # Store attr names in a callable format, i.e. 'x-init' will be accessible by {{ x_init }} when called explicitly and not in {{ attrs }}
        formatted_vars = {key.replace("-", "_"): value for key, value in c_vars.items()}
        context.update(formatted_vars)

        return self.nodelist.render(context)

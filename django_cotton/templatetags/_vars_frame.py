from django import template
from django.utils.safestring import mark_safe

from django_cotton.utils import ensure_quoted

register = template.Library()


def cotton_vars_frame(parser, token):
    """The job of the vars frame is:
    1. to filter out attributes declared as vars inside {{ attrs }} string.
    2. to provide default values to attributes.
    """
    bits = token.split_contents()[1:]  # Skip the tag name
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
        provided_attrs = context.get("attrs_dict", {})
        unprocessable = context.get("ctn_unprocessable_dynamic_attrs", set())

        # Initialize vars based on the frame's kwargs and parent attrs
        c_vars = {}
        for key, value in self.kwargs.items():
            # Check if the var exists in component attrs;
            # We have an opinion here that if the provided attr value is empty, we should use the default value
            if key in provided_attrs and key not in unprocessable:
                c_vars[key] = provided_attrs[key]
            else:
                # Attempt to resolve each kwarg value (which may include template variables)
                c_vars[key] = value.resolve(context)

        # Excluding keys from {{ attrs }} that are identified as vars
        remaining_attrs_dict = {k: v for k, v in provided_attrs.items() if k not in c_vars}
        attrs_string = " ".join(f"{k}={ensure_quoted(v)}" for k, v in remaining_attrs_dict.items())
        accessible_names = {key.replace("-", "_"): value for key, value in c_vars.items()}

        tmp_context = {
            "attrs_dict": remaining_attrs_dict,
            "attrs": mark_safe(attrs_string),
            **accessible_names,
        }

        with context.push(**tmp_context):
            return self.nodelist.render(context)

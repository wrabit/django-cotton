from django import template
from django.template.base import token_kwargs
from django.utils.safestring import mark_safe

register = template.Library()


def cotton_props_frame(parser, token):
    """The job of the props frame is to filter component kwargs (attributes) against declared props. It has to be
    second component because we desire to declare props (<c-props />) inside the component template and therefore the
    component can not manipulate its own context from it's own template, instead we declare the props frame
    directly inside component"""
    bits = token.split_contents()[1:]  # Skip the tag name
    # Parse token kwargs while maintaining token order
    tag_kwargs = token_kwargs(bits, parser)

    nodelist = parser.parse(("endcotton_props_frame",))
    parser.delete_first_token()
    return CottonPropsFrameNode(nodelist, tag_kwargs)


class CottonPropsFrameNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        # Assume 'attrs' are passed from the parent and are available in the context
        parent_attrs = context.get("attrs_dict", {})

        # Initialize props based on the frame's kwargs and parent attrs
        props = {}
        for key, value in self.kwargs.items():
            # Attempt to resolve each kwarg value (which may include template variables)
            resolved_value = value.resolve(context)
            # Check if the prop exists in parent attrs; if so, use it, otherwise use the resolved default
            if key in parent_attrs:
                props[key] = parent_attrs[key]
            else:
                props[key] = resolved_value

        # Overwrite 'attrs' in the local context by excluding keys that are identified as props
        attrs_without_props = {k: v for k, v in parent_attrs.items() if k not in props}
        context["attrs_dict"] = attrs_without_props

        # Provide all of the attrs as a string to pass to the component
        def ensure_quoted(value):
            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                return value
            else:
                return f'"{value}"'

        attrs = " ".join(
            [
                f"{key}={ensure_quoted(value)}"
                for key, value in attrs_without_props.items()
            ]
        )

        context.update({"attrs": mark_safe(attrs)})
        context.update(attrs_without_props)
        context.update(props)

        return self.nodelist.render(context)

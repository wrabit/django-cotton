from django.template import (
    Context,
    RequestContext,
    VariableDoesNotExist,
    Variable,
    Node,
    TemplateSyntaxError,
    Library,
)
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = Library()


class CottonContextMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component_stack = []
        self._cotton_dict = {}  # Separate dict for Cotton-specific data

    def __getitem__(self, key):
        if key in self._cotton_dict:
            return self._cotton_dict[key]
        print(key)
        return super().__getitem__(key)

    def push_component(self, component_key):
        self.component_stack.append(
            {
                "key": component_key,
                "attrs": {},
                "slots": {},
                "vars": {},
            }
        )

    def pop_component(self):
        return self.component_stack.pop() if self.component_stack else None

    def current_component(self):
        return self.component_stack[-1] if self.component_stack else None

    def add_attr(self, key, value):
        if self.current_component():
            self.current_component()["attrs"][key] = value

    def add_slot(self, name, content):
        if self.current_component():
            self.current_component()["slots"][name] = content

    def add_var(self, key, value):
        if self.current_component():
            self.current_component()["vars"][key] = value


class CottonContext(CottonContextMixin, Context):
    def __init__(self, dict_=None, **kwargs):
        super().__init__(dict_, **kwargs)


class CottonRequestContext(CottonContextMixin, RequestContext):
    def __init__(self, request, dict_=None, **kwargs):
        super().__init__(request, dict_, **kwargs)


def get_cotton_context_class(context: Context):
    if isinstance(context, CottonContextMixin):
        return context
    if isinstance(context, RequestContext):
        return CottonRequestContext(context.request, context)
    return CottonContext(context)


class CottonComponentNode(Node):
    def __init__(self, component_name, nodelist, attrs):
        self.component_name = component_name
        self.nodelist = nodelist
        self.attrs = attrs

    def render(self, context):
        context = get_cotton_context_class(context)

        context.push_component(self.component_name)

        # Resolve and add attributes
        resolved_attrs = {}
        for key, value in self.attrs.items():
            try:
                resolved_attrs[key] = Variable(value).resolve(context)
            except VariableDoesNotExist:
                resolved_attrs[key] = value

        # Add resolved attributes to the component context
        for key, value in resolved_attrs.items():
            context.add_attr(key, value)

        # Render the nodelist to process any slot tags and vars
        slot_content = self.nodelist.render(context)

        component = context.current_component()

        # If there's no explicit default slot, use the entire rendered content
        if "default" not in component["slots"]:
            component["slots"]["default"] = slot_content

        # Prepare attrs string, excluding vars
        attrs_dict = {
            k: v
            for k, v in resolved_attrs.items()
            if k not in component.get("vars", {})
        }
        attrs_string = " ".join(f'{k}="{v}"' for k, v in attrs_dict.items())

        ctx = Context(
            {
                **attrs_dict,  # Include attributes directly in the context
                "attrs": mark_safe(
                    attrs_string
                ),  # Keep this for backward compatibility
                "slot": component["slots"].get("default", ""),
                **component["slots"],
                **component.get("vars", {}),
            }
        )

        template_name = f"{self.component_name.replace('-', '_')}.html"
        template = get_template(template_name)

        # Use the base.Template of a backends.django.Template.
        template = get_template(template_name)
        if hasattr(template, "template"):
            template = template.template

        output = template.render(ctx)

        context.pop_component()
        return output


class CottonSlotNode(Node):
    def __init__(self, slot_name, nodelist):
        self.slot_name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        context = get_cotton_context_class(context)

        content = self.nodelist.render(context)
        if context.current_component():
            context.add_slot(self.slot_name, content)
        return ""


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


class CottonVarsNode(Node):
    def __init__(self, nodelist, var_dict):
        self.nodelist = nodelist
        self.var_dict = var_dict

    def render(self, context):
        if not isinstance(context, CottonContext):
            context = CottonContext(context)

        for key, value in self.var_dict.items():
            try:
                resolved_value = Variable(value).resolve(context)
            except VariableDoesNotExist:
                resolved_value = value
            context.add_var(key, resolved_value)

        return self.nodelist.render(context)


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

    return CottonVarsNode(nodelist, var_dict)


register.tag("cotton_component", cotton_component)
register.tag("cotton_slot", cotton_slot)
register.tag("cotton_vars", cotton_vars)

from django import template

register = template.Library()


def cotton_props(parser, token):
    # Split the token to get variable assignments
    parts = token.split_contents()
    cotton_props = {}
    for part in parts[1:]:
        key, value = part.split("=")
        cotton_props[key] = value

    return CottonPropNode(cotton_props)


class CottonPropNode(template.Node):
    def __init__(self, cotton_props):
        self.cotton_props = cotton_props

    def render(self, context):
        resolved_props = {}

        # if the same var is already set in context, it's being passed explicitly to override the cotton_var
        # if not, then we resolve it from the context
        for key, value in self.cotton_props.items():
            # if key in context:
            #     resolved_props[key] = context[key]
            #     continue
            try:
                resolved_props[key] = template.Variable(value).resolve(context)
            except (TypeError, template.VariableDoesNotExist):
                resolved_props[key] = value

        cotton_props = {"cotton_props": resolved_props}

        # Update the global context directly
        context.update(resolved_props)
        context.update(cotton_props)
        context.update({"cotton_props": resolved_props})
        context["cotton_props"].update(resolved_props)

        return ""

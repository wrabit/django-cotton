from django.template import Context, Template

from django_cotton.cotton_loader import Loader as CottonLoader


def get_compiled(template_string):
    return CottonLoader(engine=None)._compile_template_from_string(
        template_string, component_key="test_key"
    )


def get_rendered(template_string, context: dict = None):
    if context is None:
        context = {}

    compiled_string = get_compiled(template_string)

    return Template(compiled_string).render(Context(context))

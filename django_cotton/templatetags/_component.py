import ast
import functools
from enum import IntEnum
from typing import Any, NamedTuple, Union

from django.conf import settings
from django.template import Library, TemplateDoesNotExist
from django.template.base import (
    Node,
    Variable,
    VariableDoesNotExist,
    TemplateSyntaxError,
)
from django.template.context import Context, RequestContext
from django.template.loader import get_template

from django_cotton.utils import get_cotton_data
from django_cotton.exceptions import CottonIncompleteDynamicComponentError
from django_cotton.templatetags import (
    Attrs,
    InlineTemplate,
    UnprocessableDynamicAttr,
    compile_inline_template,
    snapshot_parser_library,
    strip_quotes_with_status,
)

register = Library()

_MISSING = object()


class AttrKind(IntEnum):
    BOOLEAN = 0
    ESCAPED = 1      # :: prefix (Alpine.js colon escaping) or quoted value with {{ }}/{% %}
    DYNAMIC = 2      # : prefix — explicit dynamic binding
    UNQUOTED = 3     # no quotes — treated as dynamic, falls back to string literal
    STATIC = 4


class PreparedAttr(NamedTuple):
    key: str
    kind: AttrKind
    value: Any
    compiled: Any


class PreparedValue:
    """Pre-compiled resolution chain for a dynamic attribute value.

    Created once at template parse time. At render time, resolve() tries
    each pre-built resolver in order: variable lookup, template render
    (with optional literal_eval of the result), then literal eval of the
    raw value.
    """

    __slots__ = ("raw", "_variable", "_template", "_literal")

    def __init__(self, raw: Any, *, active_library: Library | None = None) -> None:
        self.raw = raw
        self._variable = None
        self._template = None
        self._literal = _MISSING

        if not isinstance(raw, str) or not raw:
            return

        try:
            self._variable = Variable(raw)
        except (TypeError, TemplateSyntaxError):
            pass  # Not a valid variable expression, will try other resolvers

        if "{{" in raw or "{%" in raw:
            try:
                self._template = compile_inline_template(raw, active_library)
            except TemplateSyntaxError:
                pass  # Not a valid template expression, will try literal

        try:
            self._literal = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            pass  # Not a Python literal, will raise UnprocessableDynamicAttr at resolve time

    def resolve(self, context: Context) -> Any:
        """Resolve the attribute value against a template context.

        Tries each pre-built resolver in order: empty string (boolean True),
        variable lookup, template render, then literal eval. Returns the
        first successful result or raises UnprocessableDynamicAttr.
        """
        if self.raw == "":
            return True

        if self._variable is not None:
            try:
                resolved = self._variable.resolve(context)
                if isinstance(resolved, Attrs):
                    return resolved.attrs_dict()
                return resolved
            except (VariableDoesNotExist, TemplateSyntaxError):
                pass

        if self._template is not None:
            try:
                rendered = self._template.render(context)
                if rendered != self.raw:
                    try:
                        return ast.literal_eval(rendered)
                    except (ValueError, SyntaxError):
                        return rendered
            except Exception:
                pass  # Template render failed, fall through to literal resolution

        if self._literal is not _MISSING:
            return self._literal

        raise UnprocessableDynamicAttr


def _try_compile_template(value: Any, active_library: Library | None) -> InlineTemplate | None:
    """Try to compile a template from a value containing {{ }} or {% %}.
    Returns the compiled InlineTemplate or None if compilation fails or value
    has no template syntax.
    """
    if isinstance(value, str) and ("{{" in value or "{%" in value):
        try:
            return compile_inline_template(value, active_library)
        except Exception:
            pass
    return None


def _prepare_attrs(attrs: dict[str, Any], active_library: Library | None) -> list[PreparedAttr]:
    """Pre-classify and pre-compile component attributes at parse time.

    Returns a list of PreparedAttr tuples with pre-built Variable, Template,
    and literal objects so that render() only needs to call resolve/render
    on them without recreating anything.
    """
    prepared = []

    for key, raw_value in attrs.items():
        value, was_quoted = strip_quotes_with_status(raw_value)

        if value is True:
            prepared.append(PreparedAttr(key, AttrKind.BOOLEAN, True, None))

        elif key.startswith("::"):
            compiled = _try_compile_template(value, active_library)
            prepared.append(PreparedAttr(key[1:], AttrKind.ESCAPED, value, compiled))

        elif key.startswith(":"):
            pv = PreparedValue(value, active_library=active_library)
            prepared.append(PreparedAttr(key[1:], AttrKind.DYNAMIC, value, pv))

        elif not was_quoted and isinstance(value, str) and value:
            pv = PreparedValue(value, active_library=active_library)
            prepared.append(PreparedAttr(key, AttrKind.UNQUOTED, value, pv))

        else:
            compiled = _try_compile_template(value, active_library)
            kind = AttrKind.ESCAPED if compiled else AttrKind.STATIC
            prepared.append(PreparedAttr(key, kind, value, compiled))

    return prepared


class CottonComponentNode(Node):
    _vars_node_cache: dict[int, list[Node]] = {}

    def __init__(
        self,
        component_name,
        nodelist,
        attrs,
        only,
        active_library: Library | None = None,
    ):
        self.component_name = component_name
        self.nodelist = nodelist
        self.attrs = attrs
        self.template_cache = {}
        self.only = only
        self.active_library = active_library
        self._prepared_attrs = _prepare_attrs(attrs, active_library)

    def render(self, context):
        cotton_data = get_cotton_data(context)

        # Push a new component onto the stack
        component_data = {
            "key": self.component_name,
            "attrs": Attrs({}),
            "slots": {},
        }
        cotton_data["stack"].append(component_data)

        for attr in self._prepared_attrs:
            # Boolean attribute (no value, e.g. `disabled`)
            if attr.kind == AttrKind.BOOLEAN:
                component_data["attrs"][attr.key] = True

            # :: prefix (Alpine.js colon escaping) or quoted value with {{ }}/{% %}
            elif attr.kind == AttrKind.ESCAPED:
                component_data["attrs"][attr.key] = (
                    attr.compiled.render(context) if attr.compiled else attr.value
                )

            # : prefix — explicit dynamic binding
            elif attr.kind == AttrKind.DYNAMIC:
                try:
                    resolved = attr.compiled.resolve(context)
                    if attr.key == "attrs":
                        component_data["attrs"].dict.update(resolved)
                    else:
                        component_data["attrs"][attr.key] = resolved
                except UnprocessableDynamicAttr:
                    component_data["attrs"].unprocessable(attr.key)

            # No quotes — treated as dynamic, falls back to string literal
            elif attr.kind == AttrKind.UNQUOTED:
                try:
                    component_data["attrs"][attr.key] = attr.compiled.resolve(context)
                except Exception:
                    component_data["attrs"][attr.key] = attr.value

            # Plain static value
            else:
                component_data["attrs"][attr.key] = attr.value

        # Render the nodelist to process any slot tags and vars
        default_slot = self.nodelist.render(context)

        # Load the component template first
        template = self._get_cached_template(context, component_data["attrs"])

        # Exclude 'is' from attrs string output - it's only used for dynamic component resolution
        component_data["attrs"].exclude_from_string_output("is")

        # Extract vars from the component template
        vars = self._extract_vars_from_template(
            template, context, component_data["attrs"], component_data["slots"]
        )

        # Prepare the cotton-specific data
        # Vars go first so component attrs can override them
        component_state = {
            **vars,
            **component_data["slots"],
            **component_data["attrs"].make_attrs_accessible(),
            "attrs": component_data["attrs"],
            "slot": default_slot,
            "cotton_data": cotton_data,
        }

        if self.only:
            # Complete isolation
            output = template.render(Context(component_state))
        else:
            if getattr(settings, "COTTON_ENABLE_CONTEXT_ISOLATION", False) is True:
                # Default - partial isolation
                new_context = self._create_partial_context(context, component_state)
                output = template.render(new_context)
            else:
                # Legacy - no isolation
                with context.push(component_state):
                    output = template.render(context)

        cotton_data["stack"].pop()

        return output

    def _get_cached_template(self, context, attrs):
        cache = context.render_context.get(self)
        if cache is None:
            cache = context.render_context[self] = {}

        template_path = self._generate_component_template_path(self.component_name, attrs.get("is"))

        if template_path in cache:
            return cache[template_path]

        # Try to get the primary template
        try:
            template = get_template(template_path)
            if hasattr(template, "template"):
                template = template.template
            cache[template_path] = template
            return template
        except TemplateDoesNotExist:
            # If the primary template doesn't exist, try the fallback path (index.html)
            fallback_path = template_path.rsplit(".html", 1)[0] + "/index.html"

            # Check if the fallback template is already cached
            if fallback_path in cache:
                return cache[fallback_path]

            # Try to get the fallback template
            template = get_template(fallback_path)
            if hasattr(template, "template"):
                template = template.template
            cache[fallback_path] = template
            return template

    def _create_partial_context(self, original_context, component_state):
        # Get the request object from the original context
        request = original_context.get("request")

        if request:
            # Create a new RequestContext
            new_context = RequestContext(request)

            # Add the component_state to the new context
            new_context.update(component_state)
        else:
            # If there's no request object, create a simple Context
            new_context = Context(component_state)

        return new_context

    def _extract_vars_from_template(self, template, context, attrs, slots):
        """Extract vars from any CottonVarsNode instances in the template."""
        from django_cotton.templatetags._vars import CottonVarsNode

        template_id = id(template)
        vars_nodes = self._vars_node_cache.get(template_id)
        if vars_nodes is None:
            vars_nodes = [n for n in template.nodelist if isinstance(n, CottonVarsNode)]
            self._vars_node_cache[template_id] = vars_nodes

        vars = {}
        for node in vars_nodes:
            node_vars = node.extract_vars(context, attrs, slots)
            vars.update(node_vars)

        return vars

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

        component_tpl_path = component_name.replace(".", "/")

        # Cotton by default will look for snake_case version of comp names. This can be configured to allow hyphenated names.
        snaked_cased_named = getattr(settings, "COTTON_SNAKE_CASED_NAMES", True)
        if snaked_cased_named:
            component_tpl_path = component_tpl_path.replace("-", "_")

        cotton_dir = getattr(settings, "COTTON_DIR", "cotton")
        return f"{cotton_dir}/{component_tpl_path}.html"


def cotton_component(parser, token):
    """
    Parse a cotton component tag and return a CottonComponentNode.

    Uses custom parser to preserve quotes and handle template tags in attributes.
    Supports self-closing syntax: {% cotton name /%} or {% cotton name / %}
    """
    from django_cotton.tag_parser import parse_component_tag
    from django.template import NodeList

    # Check if this is a self-closing tag
    is_self_closing = token.contents.rstrip().endswith('/') or token.contents.rstrip().endswith(' /')

    # Use the custom parser that preserves quotes and handles nested template tags
    result = parse_component_tag(token.contents)

    # Snapshot the caller template's active tag/filter scope at this parse point.
    active_library = snapshot_parser_library(parser)

    if is_self_closing:
        # Self-closing tag has no content
        nodelist = NodeList()
    else:
        nodelist = parser.parse(("endcotton",))
        parser.delete_first_token()

    return CottonComponentNode(result.name, nodelist, result.attrs, result.only, active_library)

from jinja2 import Environment, PackageLoader
import web

env = Environment(loader=PackageLoader('broadgauge', 'templates'))

def render_template(_filename, **kwargs):
    """Renders a template with given filename.

    All the keyword arguments passed to this function are carried to the
    template.
    """
    template = env.get_template(_filename)
    template_vars = _get_injected_vars()
    template_vars.update(kwargs)
    return template.render(**template_vars)

def _get_injected_vars():
    if not 'injected_vars' in web.ctx:
        d = {}
        for cp in _context_processors:
            d.update(cp())
        web.ctx.injected_vars = d
    return web.ctx.injected_vars

_context_processors = []
def context_processor(f):
    """Utility to inject new variables automatically into the context
    of a template, like in Flask.
    """
    _context_processors.append(f)
    return f

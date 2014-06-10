from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('broadgauge', 'templates'))

def render_template(_filename, **kwargs):
    """Renders a template with given filename.

    All the keyword arguments passed to this function are carried to the
    template.
    """
    template = env.get_template(_filename)
    return template.render(**kwargs)
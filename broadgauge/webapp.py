import web
from . import account
from .flash import flash_processor, get_flashed_messages
from .models import  Workshop
from .oauth import get_oauth_services
from .template import render_template, context_processor
# web.config.debug = False

urls = ()

def add_urls(module):
    global urls
    module_urls = []
    for path, classname in web.group(module.urls, 2):
        classname = module.__name__ + "." + classname
        module_urls.extend([path, classname])
    urls = urls + tuple(module_urls)

def load_all_views():
    from .views import admin
    from .views import auth
    from .views import home
    from .views import orgs
    from .views import trainers
    from .views import workshops

    add_urls(admin)
    add_urls(auth)
    add_urls(home)
    add_urls(orgs)
    add_urls(trainers)
    add_urls(workshops)

load_all_views()

app = web.application(urls, globals())
app.add_processor(flash_processor)

app.notfound = lambda: web.notfound(render_template("404.html"))
app.internalerror = lambda: web.internalerror(render_template("500.html"))

@context_processor
def inject_user():
    user = account.get_current_user()
    return {
        'user': user,
        'request_path': web.ctx.path,
        'site_title': web.config.get('site_title', 'Broad Gauge'),
        'get_flashed_messages': get_flashed_messages,
        'get_oauth_services': get_oauth_services,
        'get_config': web.config.get,
        'get_pending_workshops': lambda: Workshop.findall(status='pending'),
        'get_confirmed_workshops': lambda: Workshop.findall(status='confirmed'),
    }

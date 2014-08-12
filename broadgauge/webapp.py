import web
import json

from . import account
from . import oauth
from . import forms
from .models import User, Organization, Workshop
from .template import render_template, context_processor
from .flash import flash_processor, flash, get_flashed_messages
from .sendmail import sendmail
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
    from .views import home
    from .views import orgs
    from .views import trainers
    from .views import workshops

    add_urls(admin)
    add_urls(home)
    add_urls(orgs)
    add_urls(trainers)
    add_urls(workshops)

load_all_views()

app = web.application(urls, globals())
app.add_processor(flash_processor)

@context_processor
def inject_user():
    user = account.get_current_user()
    return {
        'user': user,
        'request_path': web.ctx.path,
        'site_title': web.config.get('site_title', 'Broad Gauge'),
        'get_flashed_messages': get_flashed_messages,
        'get_pending_workshops': lambda: Workshop.findall(status='pending'),
        'get_confirmed_workshops': lambda: Workshop.findall(status='confirmed'),
    }

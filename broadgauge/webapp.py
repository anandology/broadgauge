import sys
import web
import yaml

from .template import render_template, context_processor
from . import browserid, account

web.config.debug = False

urls = (
    "/", "home",
    "/auth/login", "login",
    "/auth/logout", "logout",
)
app = web.application(urls, globals())

@context_processor
def inject_user():
    return {
        'user': account.get_current_user(),
        
        'site_title': web.config.get('site_title', 'Broad Gauge')
    }

class home:
    def GET(self):
        return render_template("home.html")

class login:
    def POST(self):
        i = web.input("assertion")
        email = browserid.verify_assertion(i.assertion)
        if email:
            account.set_login_cookie(email)
        return "ok"

class logout:
    def POST(self):
        account.logout()
        return "ok"

def load_config(configfile):
    web.config.update(yaml.load(open(configfile)))

def main():
    if "--config" in sys.argv:
        index = sys.argv.index("--config")
        configfile = sys.argv[index+1]
        sys.argv = sys.argv[:index] + sys.argv[index+2:]
        load_config(configfile)
    app.run()

if __name__ == '__main__':
    main()
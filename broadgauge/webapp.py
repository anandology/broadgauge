import sys
import web
import yaml

from . import account
from . import oauth
from . import forms
from .models import Trainer
from .template import render_template, context_processor

web.config.debug = False

urls = (
    "/", "home",
    "/logout", "logout",
    "/dashboard", "dashboard",
    "/trainers/signup", "trainer_signup",
    "/trainers/signup/(github)", "trainer_signup_redirect",
    "/oauth/github", "github_oauth_callback",
)
app = web.application(urls, globals())

@context_processor
def inject_user():
    user_email = account.get_current_user()
    # User could be either a trainer or org admin
    # The current DB schema is not flexible enough to handle that.
    # TODO: Fix the schema
    user = user_email and Trainer.find(email=user_email)
    return {
        'user': user,
        'site_title': web.config.get('site_title', 'Broad Gauge')
    }

class home:
    def GET(self):
        user = account.get_current_user()
        if user:
            raise web.seeother("/dashboard")
        else:
            return render_template("home.html")

class dashboard:
    def GET(self):
        user = account.get_current_user()
        if not user:
            raise web.seeother("/")
        return render_template("dashboard.html")

class logout:
    def POST(self):
        account.logout()
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)

class github_oauth_callback:
    def GET(self):
        i = web.input(code=None)
        if i.code:
            redirect_uri = get_oauth_redirect_url('github')            
            github = oauth.GitHub(redirect_uri)
            try:
                session = github.get_auth_session(data={'code': i.code})
                userdata = session.get('user').json()
            except KeyError:
                raise web.redirect("/trainers/signup")
            self.login(userdata)
            return web.redirect("/dashboard")

        # TODO: set error message
        raise web.redirect("/trainers/signup")

    def login(self, userdata):
        trainer = Trainer.find(email=userdata['email'])
        if not trainer:
            trainer = Trainer.new(name=userdata['name'], email=userdata['email'])
        account.set_login_cookie(trainer['email'])

class trainer_signup:
    def GET(self):
        return render_template("trainers/signup.html")

    def POST(self):
        if account.get_current_user() is None:
            return self.GET()

        i = web.input()
        form = forms.TrainerSignupForm(i)
        if not form.validate():
            return render_template("trainers/signup.html", form=form)
        raise web.seeother("/")

def get_oauth_redirect_url(provider):
    return "{home}/oauth/{provider}".format(home=web.ctx.home, provider=provider)

class trainer_signup_redirect:
    def GET(self, provider):
        if provider == 'github':
            redirect_uri = get_oauth_redirect_url('github')
            github = oauth.GitHub(redirect_uri)
            url = github.get_authorize_url()
            raise web.seeother(url)
        else:
            raise web.seeother("/trainers/signup")

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
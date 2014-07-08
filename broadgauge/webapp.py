import web
import json

from . import account
from . import oauth
from . import forms
from .models import Trainer
from .template import render_template, context_processor
from .flash import flash_processor, flash, get_flashed_messages

#web.config.debug = False

urls = (
    "/", "home",
    "/logout", "logout",
    "/dashboard", "dashboard",
    "/trainers/signup", "trainer_signup",
    "/trainers/signup/reset", "trainer_signup_reset",
    "/trainers/signup/(github)", "trainer_signup_redirect",
    "/oauth/github", "github_oauth_callback",
)
app = web.application(urls, globals())
app.add_processor(flash_processor)

@context_processor
def inject_user():
    user_email = account.get_current_user()
    # User could be either a trainer or org admin
    # The current DB schema is not flexible enough to handle that.
    # TODO: Fix the schema
    user = user_email and Trainer.find(email=user_email)
    return {
        'user': user,
        'site_title': web.config.get('site_title', 'Broad Gauge'),
        'get_flashed_messages': get_flashed_messages
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
            userdata = github.get_userdata(i.code)
            if userdata:
                # login or signup
                t = Trainer.find(email=userdata['email'])
                if t:
                    account.set_login_cookie(t.email)
                    raise web.seeother("/dashboard")
                else:
                    web.setcookie("github", json.dumps(userdata))
                    raise web.seeother("/trainers/signup")

        flash("Authorization failed, please try again.", category="error")
        raise web.seeother("/trainers/signup")

class trainer_signup:
    def GET(self): 
        form = forms.TrainerSignupForm()
        userdata = self.get_userdata()
        if userdata:
            # if already logged in, send him to dashboard
            t = Trainer.find(email=userdata['email'])
            if t:
                account.set_login_cookie(t.email)
                raise web.seeother("/dashboard")

            form.name.value = userdata['name']
        return render_template("trainers/signup.html", form=form, userdata=userdata)

    def get_userdata(self):
        userdata_json = web.cookies().get('github')
        if userdata_json:
            try:
                return json.loads(userdata_json)
            except ValueError:
                pass

    def POST(self):
        userdata = self.get_userdata()
        if not userdata:
            return self.GET()

        i = web.input()
        form = forms.TrainerSignupForm(i)
        if not form.validate():
            return render_template("trainers/signup.html", form=form)

        t = Trainer.new(name=i.name, email=userdata['email'], phone=i.phone, city=i.city, github=userdata['login'])
        account.set_login_cookie(t.email)
        raise web.seeother("/dashboard")

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

class trainer_signup_reset:
    def GET(self):
        # TODO: This should be a POST request, not GET
        web.setcookie("github", "", expires=-1)
        raise web.seeother("/trainers/signup")

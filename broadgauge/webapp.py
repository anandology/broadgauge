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

urls = (
    "/", "home",
    "/logout", "logout",
    "/login", "login",
    "/dashboard", "dashboard",
    "/trainers/signup", "trainer_signup",
    "(/trainers/signup|/orgs/signup|/login)/reset", "signup_reset",
    "(/trainers/signup|/orgs/signup|/login)/(github|google)", "signup_redirect",
    "/oauth/(github|google)", "oauth_callback",
    "/orgs/signup", "org_signup",
)

def add_urls(module):
    global urls
    module_urls = []
    for path, classname in web.group(module.urls, 2):
        classname = module.__name__ + "." + classname
        module_urls.extend([path, classname])
    urls = urls + tuple(module_urls)

def load_all_views():
    from .views import admin
    from .views import workshops
    from .views import orgs

    add_urls(admin)
    add_urls(workshops)
    add_urls(orgs)

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

class home:
    def GET(self):
        user = account.get_current_user()
        if user:
            raise web.seeother("/dashboard")
        else:
            pending_workshops = Workshop.findall(status='pending')
            upcoming_workshops = Workshop.findall(status='confirmed')
            completed_workshops = Workshop.findall(status='completed')
            return render_template("home.html",
                pending_workshops=pending_workshops,
                upcoming_workshops=upcoming_workshops,
                completed_workshops=completed_workshops)


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


class oauth_callback:
    def GET(self, service):
        i = web.input(code=None, state="/")
        if i.code:
            redirect_uri = get_oauth_redirect_url(service)
            client = oauth.oauth_service(service, redirect_uri)
            userdata = client.get_userdata(i.code)
            if userdata:
                # login or signup
                t = User.find(email=userdata['email'])
                if t:
                    account.set_login_cookie(t.email)
                    raise web.seeother("/dashboard")
                else:
                    web.setcookie("oauth", json.dumps(userdata))
                    raise web.seeother(i.state)

        flash("Authorization failed, please try again.", category="error")
        raise web.seeother(i.state)


def get_oauth_data():
    userdata_json = web.cookies().get('oauth')
    if userdata_json:
        try:
            return json.loads(userdata_json)
        except ValueError:
            pass


class login:
    def GET(self):
        userdata = get_oauth_data()
        if userdata:
            user = User.find(email=userdata['email'])
            if user:
                account.set_login_cookie(user.email)
                raise web.seeother("/dashboard")
            else:
                return render_template("login.html", userdata=userdata,
                                       error=True)
        else:
            return render_template("login.html", userdata=None)


class trainer_signup:
    FORM = forms.TrainerSignupForm
    TEMPLATE = "trainers/signup.html"

    def GET(self):
        form = self.FORM()
        userdata = get_oauth_data()
        if userdata:
            # if already logged in, send him to dashboard
            user = self.find_user(email=userdata['email'])
            if user:
                if not user.is_trainer():
                    user.make_trainer()
                account.set_login_cookie(user.email)
                raise web.seeother("/dashboard")
            form.name.value = userdata['name']
        return render_template(self.TEMPLATE, form=form, userdata=userdata)

    def POST(self):
        userdata = get_oauth_data()
        if not userdata:
            return self.GET()

        i = web.input()
        form = self.FORM(i)
        if not form.validate():
            return render_template(self.TEMPLATE, form=form)
        return self.signup(i, userdata)

    def signup(self, i, userdata):
        user = User.new(
            name=i.name,
            email=userdata['email'],
            phone=i.phone,
            city=i.city,
            github=userdata.get('github'),
            is_trainer=True)
        account.set_login_cookie(user.email)
        sendmail("emails/trainers/welcome.html",to=user.email,trainer=user)
        raise web.seeother("/dashboard")

    def find_user(self, email):
        return User.find(email=email)


class org_signup(trainer_signup):
    FORM = forms.OrganizationSignupForm
    TEMPLATE = "orgs/signup.html"

    def find_user(self, email):
        # We don't limit numer of org signups per person
        return None

    def signup(self, i, userdata):
        user = User.find(email=userdata['email'])
        if not user:
            user = User.new(name=userdata['name'], email=userdata['email'])
        org = Organization.new(name=i.name,
                               city=i.city)
        org.add_member(user, i.role)
        account.set_login_cookie(user.email)
        raise web.seeother("/orgs/{}".format(org.id))


def get_oauth_redirect_url(provider):
    home = web.ctx.home
    if provider == 'google' and home == 'http://0.0.0.0:8080':
        # google doesn't like 0.0.0.0
        home = 'http://127.0.0.1:8080'
    return "{home}/oauth/{provider}".format(home=home, provider=provider)


class signup_redirect:
    def GET(self, base, provider):
        redirect_uri = get_oauth_redirect_url(provider)
        client = oauth.oauth_service(provider, redirect_uri)
        url = client.get_authorize_url(state=base)
        raise web.seeother(url)


class signup_reset:
    def GET(self, base):
        # TODO: This should be a POST request, not GET
        web.setcookie("oauth", "", expires=-1)
        raise web.seeother(base)


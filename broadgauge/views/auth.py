import web
import json

from .. import account
from .. import oauth
from .. import forms
from ..sendmail import sendmail
from ..flash import flash
from ..models import User, Organization
from ..template import render_template

urls = (
    "/login", "login",
    "/logout", "logout",
    "/oauth/(github|google|facebook)", "oauth_callback",
    "(/trainers/signup|/orgs/signup|/login)/reset", "signup_reset",
    "(/trainers/signup|/orgs/signup|/login)/(github|google|facebook)", "signup_redirect",
    "/trainers/signup", "trainer_signup",
    "/orgs/signup", "org_signup",
)


def get_oauth_redirect_url(provider):
    home = web.ctx.home
    if provider == 'google' and home == 'http://0.0.0.0:8080':
        # google doesn't like 0.0.0.0
        home = 'http://127.0.0.1:8080'
    elif provider == 'facebook' and home == 'http://127.0.0.1:8080':
        # facebook doesn't like 127.0.0.1
        home = 'http://0.0.0.0:8080'

    return "{home}/oauth/{provider}".format(home=home, provider=provider)


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
            form.name.data = userdata['name']
            form.username.data = userdata.get('username','')
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
            username=i.username,
            phone=i.phone,
            city=i.city,
            github=userdata.get('github'),
            is_trainer=True)
        account.set_login_cookie(user.email)
        sendmail("emails/trainers/welcome.html",subject="Welcome to Python Express", to=user.email,trainer=user)
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



import web
import json

from . import account
from . import oauth
from . import forms
from .models import User, Organization, Workshop
from .template import render_template, context_processor
from .flash import flash_processor, flash, get_flashed_messages
from .views import admin

# web.config.debug = False

urls = (
    "/", "home",
    "/logout", "logout",
    "/login", "login",
    "/dashboard", "dashboard",
    "/trainers/signup", "trainer_signup",
    "/settings/profile", "edit_trainer_profile",
    "(/trainers/signup|/orgs/signup|/login)/reset", "signup_reset",
    "(/trainers/signup|/orgs/signup|/login)/(github|google)", "signup_redirect",
    "/oauth/(github|google)", "oauth_callback",
    "/orgs/signup", "org_signup",
    "/orgs/(\d+)/new-workshop", "new_workshop",
    "/orgs/(\d+)/add-member", "org_new_member",
    "/orgs/(\d+)", "org_view",
    "/orgs", "org_list",
    "/trainers", "trainers_list",
    "/trainers/(\d+)", "trainer_view",
    "/workshops/(\d+)", "workshop_view",
    "/workshops/(\d+)/express-interest", "workshop_experss_interest",
)
urls += admin.urls

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
        raise web.seeother("/dashboard")

    def find_user(self, email):
        return User.find(email=email)


class edit_trainer_profile:
    FORM = forms.TrainerEditProfileForm
    TEMPLATE = "trainers/edit-profile.html"
    def GET(self):
        user = account.get_current_user()
        if not user or not user.is_trainer():
            raise web.seeother("/")
        form = forms.TrainerEditProfileForm(user)
        return render_template(self.TEMPLATE, form=form, user=user)

    def POST(self):
        user = account.get_current_user()
        if not user or not user.is_trainer():
            raise web.seeother("/")
        i = web.input()
        form = self.FORM(i)
        if not form.validate():
            return render_template(self.TEMPLATE, form=form, user=user)
        else:
            user.update(name=i.name, city=i.city, phone=i.phone, website=i.website, bio=i.bio)
            raise web.seeother("/dashboard")


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
                               city=i.city,
                               admin_user=user,
                               role=i.role)
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


class org_list:
    def GET(self):
        orgs = Organization.findall()
        return render_template("orgs/index.html", orgs=orgs)


class org_view:
    def GET(self, id):
        org = Organization.find(id=id)
        if not org:
            raise web.notfound()

        return render_template("orgs/view.html", org=org)

class org_new_member:
    def GET(self, id):
        org = self.get_org(id)
        if not self.can_update(org):
            return render_template("permission_denied")
        else:
            form = forms.OrgAddMemberForm()
            return render_template("orgs/new-member.html", org=org, form=form)

    def POST(self, id):
        org = self.get_org(id)
        if not self.can_update(org):
            return render_template("permission_denied")
        else:
            i = web.input()
            form = forms.OrgAddMemberForm(i)
            if not form.validate():
                return render_template("orgs/new-member.html", org=org, form=form)
            else:
                member = User.find(email=i.email)
                org.add_member(member, i.role)
                flash("Successfully added {} as member.".format(member.name))
                raise web.seeother("/orgs/{}".format(org.id))

    def get_org(self, id):
        org = Organization.find(id=id)
        if not org:
            raise web.notfound()
        return org

    def can_update(self, org):
        """Returns True if the current user can update the given org.
        """
        user = account.get_current_user()
        return user and (user.is_admin() or org.is_member(user))


class trainers_list:
    def GET(self):
        trainers = User.findall(is_trainer=True)
        return render_template("trainers/index.html", trainers=trainers)


class trainer_view:
    def GET(self, id):
        trainer = User.find(id=id, is_trainer=True)
        if not trainer:
            raise web.notfound()
        return render_template("trainers/view.html", trainer=trainer)


class new_workshop:
    def GET(self, org_id):
        org = Organization.find(id=org_id)
        if not org:
            raise web.notfound()

        if not org.is_admin(account.get_current_user()):
            # TODO: display permission denied error instead
            raise web.seeother("/orgs/{}".format(org_id))

        form = forms.NewWorkshopForm()
        return render_template("workshops/new.html", org=org, form=form)

    def POST(self, org_id):
        org = Organization.find(id=org_id)
        if not org:
            raise web.notfound()
        i = web.input()
        form = forms.NewWorkshopForm(i)
        if not form.validate():
            return render_template("workshops/new.html", org=org, form=form)
        workshop = org.add_new_workshop(
            title=form.title.data,
            description=form.description.data,
            expected_participants=form.expected_participants.data,
            date=form.preferred_date.data)
        return web.seeother("/workshops/{}".format(workshop.id))


class workshop_view:
    def GET(self, id):
        workshop = Workshop.find(id=id)
        if not workshop:
            raise web.notfound()
        return render_template("workshops/view.html", workshop=workshop)

    def POST(self, id):
        workshop = Workshop.find(id=id)
        if not workshop:
            raise web.notfound()

        i = web.input(action=None)
        if i.action == "express-interest":
            return self.POST_express_interest(workshop, i)
        else:
            return render_template("workshops/view.html", workshop=workshop)

    def POST_express_interest(self, workshop, i):
        user = account.get_current_user()
        if user.is_trainer():
            workshop.record_interest(user)
            flash("Thank you for experessing interest to this workshop.")
            raise web.seeother("/workshops/{}".format(workshop.id))
        else:
            return render_template("workshops/view.html", workshop=workshop)

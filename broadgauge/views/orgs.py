import web

from .. import account
from .. import forms
from ..flash import flash
from ..models import Organization, User
from ..template import render_template


urls = (
    "/orgs", "org_list",
    "/orgs/(\d+)", "org_view",
    "/orgs/(\d+)/add-member", "org_new_member",
    "/orgs/(\d+)/new-workshop", "new_workshop",
)


def get_org(id):
    org = Organization.find(id=id)
    if not org:
        raise web.notfound()
    return org


class org_list:
    def GET(self):
        orgs = Organization.findall()
        return render_template("orgs/index.html", orgs=orgs)


class org_view:
    def GET(self, id):
        org = get_org(id)
        return render_template("orgs/view.html", org=org)


class org_new_member:
    def GET(self, id):
        org = get_org(id)
        if not self.can_update(org):
            return render_template("permission_denied.html")
        else:
            form = forms.OrgAddMemberForm()
            return render_template("orgs/new-member.html", org=org, form=form)

    def POST(self, id):
        org = get_org(id)
        if not self.can_update(org):
            return render_template("permission_denied.html")
        else:
            i = web.input()
            form = forms.OrgAddMemberForm(i)
            if not form.validate():
                return render_template("orgs/new-member.html",
                                       org=org, form=form)
            else:
                member = User.find(email=i.email)
                org.add_member(member, i.role)
                flash("Successfully added {} as member.".format(member.name))
                raise web.seeother("/orgs/{}".format(org.id))

    def can_update(self, org):
        """Returns True if the current user can update the given org.
        """
        user = account.get_current_user()
        return user and (user.is_admin() or org.is_member(user))


class new_workshop:
    def GET(self, org_id):
        org = get_org(org_id)
        if not org.can_update(account.get_current_user()):
            return render_template("permission_denied.html")

        form = forms.NewWorkshopForm()
        return render_template("workshops/new.html", org=org, form=form)

    def POST(self, org_id):
        org = get_org(org_id)
        if not org.can_update(account.get_current_user()):
            return render_template("permission_denied.html")

        i = web.input()
        form = forms.NewWorkshopForm(i)
        if not form.validate():
            return render_template("workshops/new.html", org=org, form=form)
        workshop = org.add_new_workshop(
            title=form.title.data,
            description=form.description.data,
            expected_participants=form.expected_participants.data,
            date=form.date.data)
        return web.seeother("/workshops/{}".format(workshop.id))

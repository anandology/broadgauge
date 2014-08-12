import web
from ..models import Workshop
from ..template import render_template
from ..flash import flash
from .. import account
from .. import forms


urls = (
    "/workshops/(\d+)", "workshop_view",
    "/workshops/(\d+)/edit", "edit_workshop",
)


def get_workshop(id):
    """Returns workshop by given id.

    If there is no workshop with that id, 404 error is raised.
    """
    workshop = Workshop.find(id=id)
    if not workshop:
        raise web.notfound()
    return workshop


class workshop_view:
    def GET(self, id):
        workshop = get_workshop(id=id)
        return render_template("workshops/view.html", workshop=workshop)

    def POST(self, id):
        workshop = get_workshop(id=id)
        i = web.input(action=None)
        if i.action == "express-interest":
            return self.POST_express_interest(workshop, i)
        else:
            return render_template("workshops/view.html", workshop=workshop)

    def POST_express_interest(self, workshop, i):
        user = account.get_current_user()
        if user and user.is_trainer():
            workshop.record_interest(user)
            flash("Thank you for experessing interest to conduct this workshop.")
            raise web.seeother("/workshops/{}".format(workshop.id))
        else:
            return render_template("workshops/view.html", workshop=workshop)


class edit_workshop:
    def GET(self, workshop_id):
        workshop = get_workshop(id=id)
        self.ensure_updatable(workshop)

        org = workshop.get_org()
        if not org.can_update(account.get_current_user()):
            return render_template("permission_denied.html")

        form = forms.NewWorkshopForm(workshop.dict())
        return render_template("workshops/edit.html",
                               org=org, workshop=workshop, form=form)

    def POST(self, workshop_id):
        workshop = get_workshop(id=id)
        org = workshop.get_org()
        if not org.can_update(account.get_current_user()):
            return render_template("permission_denied.html")

        i = web.input()
        form = forms.NewWorkshopForm(i)
        if not form.validate():
            return render_template("workshops/edit.html",
                                   org=org, workshop=workshop, form=form)
        else:
            workshop.update(
                title=i.title,
                description=i.description,
                expected_participants=i.expected_participants,
                date=i.date)
            flash("Thanks for updating the workshop details.")
            return web.seeother("/workshops/{}".format(workshop.id))

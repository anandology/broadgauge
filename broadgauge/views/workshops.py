import web
from ..models import User, Workshop
from ..template import render_template
from ..flash import flash
from .. import account
from .. import forms


urls = (
    "/workshops/(\d+)", "workshop_view",
    "/workshops/(\d+)/edit", "workshop_edit",
    "/workshops/(\d+)/set-trainer", "workshop_set_trainer",
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


class workshop_edit:
    def GET(self, workshop_id):
        workshop = get_workshop(id=workshop_id)

        org = workshop.get_org()
        if not org.can_update(account.get_current_user()):
            return render_template("permission_denied.html")

        if web.ctx.method == 'POST':
            i = web.input()
            form = forms.NewWorkshopForm(i)
            if form.validate():
                workshop.update(
                    title=i.title,
                    description=i.description,
                    expected_participants=i.expected_participants,
                    date=i.date)
                flash("Thanks for updating the workshop details.")
                return web.seeother("/workshops/{}".format(workshop.id))
        else:
            form = forms.NewWorkshopForm(workshop.dict())
        return render_template("workshops/edit.html",
                               org=org, workshop=workshop, form=form)

    POST = GET

class workshop_set_trainer:
    def GET(self, workshop_id):
        workshop = get_workshop(id=workshop_id)
        user = account.get_current_user()
        if not user or not user.is_admin():
            return render_template("permission_denied.html")

        form = forms.WorkshopSetTrainerForm(web.input())
        if web.ctx.method == "POST" and form.validate():
            trainer = User.find(email=form.email.data)
            workshop.set_trainer(trainer)
            flash("Thanks for setting the trainer for this workshop.")
            raise web.seeother("/workshops/{}".format(workshop.id))
        return render_template("workshops/set-trainer.html",
                               workshop=workshop, form=form)

    POST = GET

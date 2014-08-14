import web

from .. import account
from .. import forms
from ..models import User
from ..models import Workshop
from ..template import render_template


urls = (
    "/trainers", "trainers_list",
    "/trainers/(.+)", "trainer_view",
    "/settings/profile", "edit_trainer_profile",
)


class trainers_list:
    def GET(self):
        trainers = User.findall(is_trainer=True)
        return render_template("trainers/index.html", trainers=trainers)


class trainer_view:
    def GET(self, username):
        trainer = User.find(username=username, is_trainer=True)
        if not trainer:
            raise web.notfound()
        upcoming_workshops = Workshop.findall(status='confirmed', trainer_id=trainer.id)
        completed_workshops = Workshop.findall(status='completed', trainer_id=trainer.id)
        return render_template("trainers/view.html",
                               upcoming_workshops=upcoming_workshops,
                               completed_workshops=completed_workshops,
                               trainer=trainer)


class edit_trainer_profile:
    def GET(self):
        user = account.get_current_user()
        if not user or not user.is_trainer():
            raise web.seeother("/")

        i = web.input()
        form = forms.TrainerEditProfileForm(i)

        if web.ctx.method == 'POST' and form.validate():
            user.update(name=i.name, city=i.city, phone=i.phone, website=i.website, bio=i.bio)
            raise web.seeother("/dashboard")
        else:
            return render_template("trainers/edit-profile.html", form=form, user=user)

    POST = GET

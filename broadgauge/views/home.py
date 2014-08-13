import web

from .. import account
from ..models import Workshop
from ..template import render_template


urls = (
    "/", "home",
    "/dashboard", "dashboard",
)

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
        upcoming_workshops = Workshop.findall(status='confirmed', trainer_id=user.id)
        return render_template("dashboard.html",
                               upcoming_workshops=upcoming_workshops)


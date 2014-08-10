import functools
import web

from ..template import render_template
from ..models import User
from ..flash import flash
from .. import account


modname = __name__
urls = (
    "/admin", modname + ".admin",
)

def has_admins():
    """Returns True if there is at least one admin defined.
    """
    admins = User.findall(is_admin=True)
    return bool(admins)

def admin_required(f):
    def is_current_user_admin():
        user = account.get_current_user()
        if not user:
            return False

        if user.is_admin():
            return True

        # Bootstrap Mode
        # when there are no admins defined, consider everyone an admin.
        if user and not User.findall(is_admin=True):
            return True

    @functools.wraps(f)
    def g(*a, **kw):
        if is_current_user_admin():
            return f(*a, **kw)
        else:
            return render_template("permission_denied.html")
    return g

class admin:
    @admin_required
    def GET(self):
        admins = User.findall(is_admin=True)
        return render_template("admin/index.html", admins=admins)

    @admin_required
    def POST(self):
        i = web.input(action=None)
        if i.action == "add-admin" and 'email' in i:
            user = User.find(email=i.email)
            if user:
                user.update(is_admin=True)
                flash('Succefully marked {} as admin'.format(i.email))
                raise web.seeother("/admin")
            else:
                admins = User.findall(is_admin=True)                
                return render_template("admin/index.html", 
                        admins=admins, 
                        error_add_admin="Not a valid user.")
        else:
            return self.GET()

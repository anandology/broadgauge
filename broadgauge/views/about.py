import web

from .. import account
from .. import forms
from ..flash import flash
from ..template import render_template


urls = (
    "/about", "about_view"
)


class about_view:
    def GET(self):
        md = render_template("about.md")
        return render_template("about.html", content=md)

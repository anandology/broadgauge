import web
from template import render_template

web.config.debug = False

urls = (
    "/", "home",
)
app = web.application(urls, globals())

class home:
    def GET(self):
        return render_template("home.html")

if __name__ == '__main__':
    app.run()
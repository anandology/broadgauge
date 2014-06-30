import sys
import web
import yaml

from .template import render_template, context_processor

web.config.debug = False

urls = (
    "/", "home",
)
app = web.application(urls, globals())

@context_processor
def inject_user():
    return {
        'user': account.get_current_user(),
        'site_title': web.config.get('site_title', 'Broad Gauge')
    }

class home:
    def GET(self):
        return render_template("home.html")

def load_config(configfile):
    web.config.update(yaml.load(open(configfile)))

def main():
    if "--config" in sys.argv:
        index = sys.argv.index("--config")
        configfile = sys.argv[index+1]
        sys.argv = sys.argv[:index] + sys.argv[index+2:]
        load_config(configfile)
    app.run()

if __name__ == '__main__':
    main()
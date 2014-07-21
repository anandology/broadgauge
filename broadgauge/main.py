import os
import sys
import web
import yaml
from . import default_settings


def load_default_config():
    # take all vars defined in default_config
    config = dict((k, v) for k, v in default_settings.__dict__.items()
                  if not k.startswith("_"))
    web.config.update(config)


def load_config_from_env():
    keys = [
        'SITE_TITLE',
        'GITHUB_CLIENT_ID',
        'GITHUB_CLIENT_SECRET',
        'SECRET_KEY',
        'DATABASE_URL',
        'ADMIN_USER',
    ]

    for k in keys:
        if k in os.environ:
            web.config[k.lower()] = os.environ[k]

load_default_config()
load_config_from_env()
from . import webapp
application = webapp.app.wsgifunc()

# Heroku doesn't handle static files, use StaticMiddleware.
application = web.httpserver.StaticMiddleware(application)


def load_config_from_file(configfile):
    web.config.update(yaml.load(open(configfile)))


def main():
    if "--config" in sys.argv:
        index = sys.argv.index("--config")
        configfile = sys.argv[index+1]
        sys.argv = sys.argv[:index] + sys.argv[index+2:]
        load_config_from_file(configfile)

    webapp.app.run()


if __name__ == '__main__':
    main()

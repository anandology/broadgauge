import os
import sys
import web
import yaml
import logging
from . import default_settings

# load actions
from . import actions

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
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'FACEBOOK_CLIENT_ID',
        'FACEBOOK_CLIENT_SECRET',
        'SECRET_KEY',
        'DATABASE_URL',
        'ADMIN_USER',
        'SMTP_SERVER',
        'SMTP_POST',
        'SMTP_USERNAME',
        'SMTP_PASSWORD',
        'SMTP_STARTTLS',
        'FROM_ADDRESS',
        'CONTACT_EMAIL'
    ]

    for k in keys:
        if k in os.environ:
            web.config[k.lower()] = os.environ[k]

    # auto add all keys for format BROADGAUGE_xxx to config
    for k in os.environ:
        if k.startswith('BROADGAUGE_'):
            k2 = k[len('BROADGAUGE_'):].lower()
            web.config[k2] = os.environ[k]

load_default_config()
load_config_from_env()
from . import webapp
from . import utils

# send email on every internal error
utils.setup_error_emails(webapp.app)

application = webapp.app.wsgifunc()

# Heroku doesn't handle static files, use StaticMiddleware.
application = web.httpserver.StaticMiddleware(application)


def load_config_from_file(configfile):
    web.config.update(yaml.load(open(configfile)))

def setup_logging():
    FORMAT = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

def main():
    if "--config" in sys.argv:
        index = sys.argv.index("--config")
        configfile = sys.argv[index+1]
        sys.argv = sys.argv[:index] + sys.argv[index+2:]
        load_config_from_file(configfile)

    setup_logging()
    webapp.app.run()


if __name__ == '__main__':
    main()

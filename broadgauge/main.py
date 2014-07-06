import web
import os

def read_config_from_env():
    keys = [
        'SITE_TITLE',
        'GITHUB_CLIENT_ID',
        'GITHUB_CLIENT_SECRET',
        'SECRET_KEY',
        'DATABASE_URL'
    ]

    for k in keys:
        if k in os.environ:
            web.config[k.lower()] = os.environ[k]


read_config_from_env()
from . import webapp
application = webapp.app.wsgifunc()

# Heroku doesn't handle static files, use StaticMiddleware.
application = web.httpserver.StaticMiddleware(application)

if __name__ == '__main__':
    webapp.main()
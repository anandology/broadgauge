"""OAuth integration for web.py.

This will be made a separate project once it is ready.
"""
from rauth import OAuth2Service
import web

class GitHub(OAuth2Service):
    def __init__(self, redirect_uri):
        OAuth2Service.__init__(self, 
            client_id=web.config.github_client_id,
            client_secret=web.config.github_client_secret,
            name='github',
            authorize_url='https://github.com/login/oauth/authorize',
            access_token_url='https://github.com/login/oauth/access_token',
            base_url='https://api.github.com/')
        self.redirect_uri = redirect_uri
        print "github", redirect_uri

    def get_authorize_url(self, **params):
        params.setdefault('response_type', 'code')
        params.setdefault('redirect_uri', self.redirect_uri)
        return OAuth2Service.get_authorize_url(self, **params)

    def get_auth_session(self, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            kwargs['data'].setdefault('redirect_uri', self.redirect_uri)
        return OAuth2Service.get_auth_session(self, **kwargs)
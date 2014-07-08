"""OAuth integration.
"""
from rauth import OAuth2Service
import web
import logging

logger = logging.getLogger(__name__)

class GitHub(OAuth2Service):
    """GitHub OAuth integration.
    """
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

    def get_userdata(self, code):
        """Returns the relevant userdata from github.

        This function must be called from githun oauth callback
        and the auth code must be passed as argument.
        """
        try:
            session = self.get_auth_session(data={'code': code})
            d = session.get('user').json()
            return dict(name=d['name'], email=d['email'], login=d['login'])            
        except KeyError, e:
            logger.error("failed to get user data from github. Error: %s", str(e))

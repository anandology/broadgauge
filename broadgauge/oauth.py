"""OAuth integration.
"""
from rauth import OAuth2Service
import web
import logging
import json

logger = logging.getLogger(__name__)


def oauth_service(service, redirect_uri):
    if service == 'github':
        return GitHub(redirect_uri)
    elif service == 'google':
        return Google(redirect_uri)
    elif service == 'facebook':
        return Facebook(redirect_uri)


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

    def get_authorize_url(self, **params):
        params.setdefault('response_type', 'code')
        params.setdefault('redirect_uri', self.redirect_uri)
        params.setdefault('scope', 'user:email')
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
            email = self.get_verified_email(session)
            if not email:
                logger.error("No verified email found for this user {}".format(d['login']))
                return
            return dict(
                name=d["name"],
                email=email,
                username=d["login"],
                github=d["login"],
                service="GitHub")
        except KeyError, e:
            logger.error("failed to get user data from github. Error: %s",
                         str(e))

    def get_verified_email(self, session):
        """Finds verified email of the user using oauth session.
        """
        data = session.get('https://api.github.com/user/emails').json()
        emails = [d['email'] for d in data if d['verified'] and d['primary']]
        if emails:
            return emails[0]


class Google(OAuth2Service):
    """Google OAuth integration.
    """
    def __init__(self, redirect_uri):
        OAuth2Service.__init__(self,
            client_id=web.config.google_client_id,
            client_secret=web.config.google_client_secret,
            name='google',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://www.googleapis.com/oauth2/v1/')
        self.redirect_uri = redirect_uri

    def get_authorize_url(self, **params):
        params.setdefault('response_type', 'code')
        params.setdefault('redirect_uri', self.redirect_uri)
        params.setdefault('scope', 'profile email')
        return OAuth2Service.get_authorize_url(self, **params)

    def get_auth_session(self, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            kwargs['data'].setdefault('redirect_uri', self.redirect_uri)
            kwargs['data'].setdefault('grant_type', 'authorization_code')
            print kwargs
        return OAuth2Service.get_auth_session(self, **kwargs)

    def get_userdata(self, code):
        """Returns the relevant userdata from github.

        This function must be called from githun oauth callback
        and the auth code must be passed as argument.
        """
        try:
            session = self.get_auth_session(data={'code': code},
                                            decoder=json.loads)
            d = session.get('userinfo').json()
            # suggest basename of the email as username
            username = d['email'].split("@")[0]
            return dict(
                name=d['name'],
                email=d['email'],
                username=username,
                service='Google')
        except KeyError, e:
            logger.error("failed to get user data from google. Error: %s",
                         str(e), exc_info=True)

class Facebook(OAuth2Service):
    """Facebook OAuth integration.
    """
    def __init__(self, redirect_uri):
        OAuth2Service.__init__(self,
            client_id=web.config.facebook_client_id,
            client_secret=web.config.facebook_client_secret,
            name='facebook',
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/')
        self.redirect_uri = redirect_uri

    def get_authorize_url(self, **params):
        params.setdefault('response_type', 'code')
        params.setdefault('redirect_uri', self.redirect_uri)
        params.setdefault('scope', 'email')
        return OAuth2Service.get_authorize_url(self, **params)

    def get_auth_session(self, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            kwargs['data'].setdefault('redirect_uri', self.redirect_uri)
            kwargs['data'].setdefault('grant_type', 'authorization_code')
        return OAuth2Service.get_auth_session(self, **kwargs)

    def get_userdata(self, code):
        """Returns the relevant userdata from github.

        This function must be called from githun oauth callback
        and the auth code must be passed as argument.
        """
        try:
            session = self.get_auth_session(
                    data={'code': code, 'redirect_uri': self.redirect_uri})
            d = session.get('me').json()
            # suggest basename of the email as username
            username = d['email'].split("@")[0]
            return dict(
                name=d['name'],
                email=d['email'],
                username=username,
                service='Facebook')
        except KeyError, e:
            logger.error("failed to get user data from facebook. Error: %s",
                         str(e), exc_info=True)

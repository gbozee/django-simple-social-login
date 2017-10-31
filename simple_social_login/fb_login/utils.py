import requests
from django.utils import timezone
from . import signals as fb_signals
import datetime
from . import settings
from django.contrib.sites.models import Site
from django.shortcuts import reverse

def date_to_expire(sec):
    return timezone.now() + \
        datetime.timedelta(seconds=sec)


class FacebookAPI(object):
    def __init__(self):
        self.base_url = 'https://graph.facebook.com/{}'.format(
            settings.FACEBOOK_APP_VERSION)
        self.client_id = settings.FACEBOOK_APP_ID
        self.client_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_url = settings.FACEBOOK_REDIRECT_URL

    def make_response(self, method, path, **kwargs):
        options = {
            'GET': requests.get,
            'POST': requests.post
        }
        params = kwargs.get('params', {})
        params.update(
            client_id=self.client_id,
            client_secret=self.client_secret)
        return options[method]("{}{}".format(self.base_url, path), **kwargs)

    def get_long_lived_access_token(self, access_token, request=None):
        """
        response is of this form
        {
            "access_token","token_type", "expires_in"
        }
        """
        if not self.redirect_url:
            current = Site.objects.get_current(request=request)
            self.redirect_url = "https://{}{}".format(
                current.domain, reverse('fb_login:fb_redirect_uri'))
        response = self.make_response('GET', '/oauth/access_token', params={
            'grant_type': "fb_exchange_token",
            'fb_exchange_token': access_token
        })
        if response.status_code < 400:
            token_data = response.json()
            expires_at = timezone.now() + \
                datetime.timedelta(seconds=token_data['expires_in'])
            access_token = token_data['access_token']
            fb_signals.save_long_lived_token.send(
                sender=None, request=request, access_token=access_token,
                expires_at=expires_at)
            return self.get_authorization_code(access_token)
        response.raise_for_status()

    def get_authorization_code(self, long_lived_token):
        response = self.make_response('GET', '/oauth/client_code', params={
            'access_token': long_lived_token,
            'redirect_uri': self.redirect_url
        })
        if response.status_code < 400:
            return response.json()['code']
        response.raise_for_status()

from django.conf import settings
import requests
from django.utils import timezone
from . import signals as fb_signals
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests


class GoogleAPIError(Exception):
    pass


class GoogleAPI(object):
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID

    def verify_token(self, token, request=None):
        try:
            idinfo = id_token.verify_oauth2_token(
                token, g_requests.Request(), self.client_id)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise GoogleAPIError('Wrong issuer.')

            userid = idinfo['sub']
            data = {
                'email': idinfo.get('email'),
                'first_name': idinfo.get('given_name'),
                'last_name': idinfo.get('family_name')
            }
            fb_signals.data_from_google_scope.send(sender=None, data=data,request=request)
            return data
        except ValueError:
            # Invalid token
            raise GoogleAPIError("The token sent to the server is invalid")


class AccountKitAPI(object):
    def __init__(self):
        self.base_url = "https://graph.accountkit.com/{}".format(
            settings.FACEBOOK_ACCOUNT_KIT_API_VERSION)
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_ACCOUNT_KIT_APP_SECRET
        self.app_access_token = "|".join(['AA', self.app_id, self.app_secret])

    def make_response(self, method, path, **kwargs):
        options = {
            'GET': requests.get,
            'POST': requests.post
        }
        params = kwargs.get('params', {})
        return options[method]("{}{}".format(self.base_url, path), **kwargs)

    def get_access_token(self, code):
        """
        return {id,'access_token,'token_refresh_interval_sec"""
        params = {
            "grant_type": 'authorization_code',
            "code": code,
            "access_token": self.app_access_token
        }
        # import pdb; pdb.set_trace()
        response = self.make_response('GET', '/access_token', params=params)
        if response.status_code < 400:
            data = response.json()
            expires_at = date_to_expire(data['token_refresh_interval_sec'])
            access_token = data['access_token']
            user_data = self.get_user_details(access_token)
            new_data = {
                'user_id': data['id']
            }
            if user_data.get('email'):
                new_data.update(email=user_data['email']['address'])
            if user_data.get('phone'):
                new_data.update(number=user_data['phone']['number'])
            fb_signals.account_kit_access_token.send(
                sender=None, access_token=access_token, expires_at=expires_at,
                data=new_data)
            return new_data
        response.raise_for_status()

    def get_user_details(self, access_token):
        """
        {'id', 'phone': {'number'}, 'application': {'id'}}
        """
        response = self.make_response('GET', '/me', params={
            "access_token": access_token,
            'appsecret_proof': sign_request(self.app_secret, access_token)
        })
        if response.status_code < 400:
            return response.json()
        response.raise_for_status()


def date_to_expire(sec):
    return timezone.now() + \
        datetime.timedelta(seconds=sec)


def sign_request(key, raw):
    from hashlib import sha256
    import hmac
    h = hmac.new(
        key.encode('utf-8'),
        msg=raw.encode('utf-8'),
        digestmod=sha256
    )
    return h.hexdigest()


class FacebookAPI(object):
    def __init__(self):
        self.base_url = 'https://graph.facebook.com/v2.10'
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

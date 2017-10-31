import requests
from . import settings
from django.utils import timezone
import datetime
from . import signals as fb_signals

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


class AccountKitAPI(object):
    def __init__(self):
        self.base_url = "https://graph.accountkit.com/{}".format(
            settings.FACEBOOK_ACCOUNT_KIT_API_VERSION)
        self.app_id = settings.FACEBOOK_ACCOUNT_KIT_APP_ID
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

from . import settings
from . import signals as fb_signals
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

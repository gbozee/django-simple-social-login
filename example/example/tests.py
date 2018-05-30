from django.test import TestCase
import json
try:
    from unittest import mock
except ImportError:
    import mock
from simple_social_login.account_kit.utils import sign_request, date_to_expire
from django.dispatch import receiver
from simple_social_login.account_kit import signals as account_kit_signals
from simple_social_login.fb_login import signals as fb_signals
from simple_social_login.google_login import signals as google_signals
from django.shortcuts import reverse
from django.conf import settings
import datetime


@receiver(account_kit_signals.account_kit_access_token)
def signal_called(sender, **kwargs):
    generic_function(access_token=kwargs.get('access_token'),
                     expires_at=kwargs.get('expires_at'), data=kwargs.get('data'))


def generic_function(**params):
    print(params)


@receiver(fb_signals.data_from_fb_scope)
def signal_called_2(sender, **kwargs):
    generic_function(data=kwargs.get('data'))


@receiver(fb_signals.save_long_lived_token)
def signal_called_3(sender, **kwargs):
    generic_function(access_token=kwargs.get('access_token'),
                     expires_at=kwargs.get('expires_at'))


@receiver(google_signals.data_from_google_scope)
def signal_called4(sender, **kwargs):
    generic_function(data=kwargs.get('data'))


class MockRequest:

    def __init__(self, response, **kwargs):
        self.response = response
        self.overwrite = False
        if kwargs.get('overwrite'):
            self.overwrite = True
        self.status_code = kwargs.get('status_code', 200)

    @classmethod
    def raise_for_status(cls):
        pass

    def json(self):
        if self.overwrite:
            return self.response
        return {'data': self.response}


class SocialAPITestCase(TestCase):
    def setUp(self):
        self.patcher = mock.patch(
            'simple_social_login.tests.generic_function')
        self.mocker = self.patcher.start()
        self.mock_patcher = mock.patch(
            'requests.get'
        )
        self.mock_get = self.mock_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.mock_get.stop()

    def account_kit_action(self, callback):
        self.mock_get.return_value = self.mock_response({
            'id': "ab",
            "access_token": "cd",
            "token_refresh_interval_sec": 30,
            "phone": {
                "number": "+234232323223",

            },
            'application': {
                'id': 23
            },
            'email': {
                "address": "j@example.com"
            }
        })
        response = callback()
        access_token = "|".join(
            ['AA', settings.FACEBOOK_ACCOUNT_KIT_APP_ID, settings.FACEBOOK_ACCOUNT_KIT_APP_SECRET])
        # import pdb; pdb.set_trace()
        self.mock_get.assert_has_calls([
            mock.call("https://graph.accountkit.com/v1.2/access_token", params={
                'grant_type': "authorization_code",
                "code": "12345",
                'access_token': access_token
            }),
            mock.call("https://graph.accountkit.com/v1.2/me", params={
                'access_token': "cd",
                'appsecret_proof': sign_request(settings.FACEBOOK_ACCOUNT_KIT_APP_SECRET, "cd")
            })
        ])
        self.mocker.assert_called_once_with(
            access_token='cd', expires_at=date_to_expire(30),
            data={
                'user_id': "ab",
                "email": "j@example.com",
                "number": "+234232323223"
            })
        return response

    def post(self, url, **kwargs):
        return self.client.post(url, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                **kwargs)

    @mock.patch("simple_social_login.account_kit.utils.timezone.now")
    def test_account_kit_validates_request(self, mock_time_zone):
        mock_time_zone.return_value = datetime.datetime(2016, 10, 12, 3, 4, 2)
        url = reverse('account_kit:verify')

        self.account_kit_action(
            lambda: self.post(url, data=json.dumps({'code': "12345"})))

    @mock.patch("simple_social_login.account_kit.utils.timezone.now")
    def test_account_kit_redirect_url_navigates_correctly(self, mock_time_zone):
        mock_time_zone.return_value = datetime.datetime(2016, 10, 12, 3, 4, 2)

        url = reverse('account_kit:redirect')
        response = self.account_kit_action(
            lambda: self.client.get(url, data={'code': "12345"})
        )
        result = self.client.get(response.url, data={'code': "12345"})
        self.assertEqual(result.json(), {
            'user_id': 'ab', 'email': "j@example.com", 'number': "+234232323223"
        })

    def facebook_action(self, callback):
        self.mock_get.return_value = self.mock_response({
            "access_token": "cd",
            "token_type": "bearer",
            'expires_in': 30,
            'code': "cdesfe"
        })
        response = callback()
        self.mock_get.assert_has_calls([mock.call(
            "https://graph.facebook.com/v2.10/oauth/access_token",
            params={
                'grant_type': "fb_exchange_token",
                'fb_exchange_token': "1234",
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET
            }),
            mock.call("https://graph.facebook.com/v2.10/oauth/client_code", params={
                'access_token': "cd",
                'redirect_uri': settings.FACEBOOK_REDIRECT_URL,
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET
            })]
        )
        self.mocker.assert_has_calls([
            mock.call(data={
                "name": "johndoe"
            }),
            mock.call(access_token="cd", expires_at=date_to_expire(30))
        ])

    @mock.patch("simple_social_login.fb_login.utils.timezone.now")
    def test_facebook_login_validation(self, mock_time_zone):
        mock_time_zone.return_value = datetime.datetime(2016, 10, 12, 3, 4, 2)
        url = reverse('fb_login:verify')
        self.facebook_action(lambda: self.post("{}?access_token={}".format(url, "1234"), data=json.dumps({
            "name": "johndoe"
        })))

    def test_facebook_redirect_url_navigates_correctly(self):
        url = reverse("fb_login:fb_redirect_uri")
        response = self.client.get(url)
        response = self.client.get(response.url)
        self.assertEqual(response.json(), {})

    @mock.patch('simple_social_login.google_login.utils.id_token.verify_oauth2_token')
    def test_google_login_validation(self, mock_request):
        mock_request.return_value = {
            'email': "j@example.com",
            'iss': "accounts.google.com",
            'given_name': "Devato",
            'family_name': "Soli",
            'sub': "23",
        }
        url = reverse('google_login:verify')
        response = self.post(url, data=json.dumps({
            'token': "234911"
        }))
        self.mocker.assert_called_once_with(data={
            'email': "j@example.com",
            'first_name': "Devato",
            'last_name': "Soli"
        })

    def test_google_redirect_url_navigates_correctly(self):
        url = reverse('google_login:google_redirect_uri')
        response = self.client.get(url)
        response = self.client.get(response.url)
        self.assertEqual(response.json(), {})

    def mock_response(self, data, **kwargs):
        return MockRequest(data, overwrite=True, ** kwargs)

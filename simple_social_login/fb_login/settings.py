from django.conf import settings

FB_URL_ON_SUCCESS = getattr(
    settings, 'FB_URL_ON_SUCCESS', 'fb_login:redirect_on_success')
FACEBOOK_APP_ID = getattr(
    settings, "FACEBOOK_APP_ID", None
)
FACEBOOK_ACCOUNT_KIT_API_VERSION = getattr(
    settings, 'FACEBOOK_ACCOUNT_KIT_API_VERSION', "v1.2")

FACEBOOK_APP_SECRET = getattr(
    settings, 'FACEBOOK_APP_SECRET', None
)
FACEBOOK_REDIRECT_URL = getattr(
    settings, "FACEBOOK_REDIRECT_URL", None
)
FACEBOOK_APP_VERSION = getattr(settings, "FACEBOOK_APP_VERSION", "v2.10")


def create_user(cls, **user_data):
    return cls.objects.create(
        username=user_data['email'], email=user_data['email'],
        first_name=user_data['name'])


FB_CREATE_USER_CALLBACK = getattr(
    settings, "FB_CREATE_USER_CALLBACK", create_user)

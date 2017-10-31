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

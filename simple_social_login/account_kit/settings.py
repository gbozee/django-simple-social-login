from django.conf import settings

ACCOUNT_KIT_URL_ON_SUCCESS = getattr(
    settings, 'ACCOUNT_KIT_URL_ON_SUCCESS', 'account_kit:redirect_on_success')
FACEBOOK_ACCOUNT_KIT_APP_ID = getattr(
    settings, "FACEBOOK_APP_ID", None
)
FACEBOOK_ACCOUNT_KIT_APP_SECRET = getattr(
    settings, "FACEBOOK_ACCOUNT_KIT_APP_SECRET", None
)
FACEBOOK_ACCOUNT_KIT_API_VERSION = getattr(
    settings, 'FACEBOOK_ACCOUNT_KIT_API_VERSION', "v1.2")

FACEBOOK_ACCOUNT_KIT_REDIRECT_URL = getattr(
    settings, 'FACEBOOK_ACCOUNT_KIT_REDIRECT_URL', None
)

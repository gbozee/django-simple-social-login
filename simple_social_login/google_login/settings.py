from django.conf import settings

GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)
GOOGLE_URL_ON_SUCCESS = getattr(
    settings, "GOOGLE_URL_ON_SUCCESS", "google_login:redirect_on_success")

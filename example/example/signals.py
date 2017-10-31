
from django.dispatch import Signal
data_from_fb_scope = Signal(providing_args=["request", "data"])
save_long_lived_token = Signal(
    providing_args=['request', "access_token", "expires_at"])
account_kit_access_token = Signal(
    providing_args=['access_token', 'expires_at',
                    'data']
)
data_from_google_scope = Signal(providing_args=['request', 'data'])

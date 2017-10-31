from django.dispatch import Signal

account_kit_access_token = Signal(
    providing_args=['access_token', 'expires_at',
                    'data']
)


from django.dispatch import Signal
data_from_google_scope = Signal(providing_args=['request', 'data'])
after_creating_google_user = Signal(providing_args=['request'])

from django.conf import settings

GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)


def create_user(cls, **user_data):
    return cls.objects.create(
        username=user_data['email'], email=user_data['email'],
        first_name=user_data['first_name'], last_name=user_data['last_name'])


GOOGLE_URL_ON_SUCCESS = getattr(
    settings, "GOOGLE_URL_ON_SUCCESS", "google_login:redirect_on_success")
GOOGLE_CREATE_USER_CALLBACK = getattr(
    settings, "GOOGLE_CREATE_USER_CALLBACK", create_user)

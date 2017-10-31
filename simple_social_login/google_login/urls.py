
from django.conf.urls import url
from django.http import JsonResponse
from . import settings
import json
from . import signals as fb_signals
from .utils import GoogleAPI
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from django.shortcuts import reverse
from . import signals as google_signals
from django.contrib.auth import get_user_model, login
from . import settings

@receiver(google_signals.data_from_google_scope)
def onGoogleData(sender, request, data, **kwargs):
    User = get_user_model()
    result = User.objects.filter(email=data['email']).first()
    if not result:
        result = settings.GOOGLE_CREATE_USER_CALLBACK(User, **data)
    result.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, result)


def create_or_update_google_user(request):
    data = {}
    if request.is_ajax():
        data = json.loads(request.body)
        google = GoogleAPI()
        data = google.verify_token(data['token'], request=request)
    return JsonResponse(data)


class SuccessView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if settings.GOOGLE_URL_ON_SUCCESS == 'google_login:redirect_on_success':
            return reverse(settings.GOOGLE_URL_ON_SUCCESS)
        return settings.GOOGLE_URL_ON_SUCCESS


def redirect_uri(request):
    return JsonResponse(request.GET.dict())


urlpatterns = [
    url(r'^validate/$', csrf_exempt(create_or_update_google_user),
        name="verify"),
    url(r'^redirect/$', SuccessView.as_view(), name='google_redirect_uri'),
    url(r'^redirect-view/$', redirect_uri, name='redirect_on_success')
]

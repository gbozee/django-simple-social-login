
from django.conf.urls import url
from django.contrib import admin
from django.http import JsonResponse
from . import settings
from .utils import AccountKitAPI
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
import json
from django.shortcuts import reverse


def reusable(data):
    account_kit = AccountKitAPI()
    return account_kit.get_access_token(data['code'])


def account_kit_authenticate(request):
    data = {}
    if request.is_ajax():
        data = json.loads(request.body)
        data = reusable(data)
    return JsonResponse(data)


class SuccessView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        data = reusable(self.request.GET.dict())
        if settings.ACCOUNT_KIT_URL_ON_SUCCESS == 'account_kit:redirect_on_success':
            return reverse(settings.ACCOUNT_KIT_URL_ON_SUCCESS)
        return settings.ACCOUNT_KIT_URL_ON_SUCCESS


def redirect_uri(request):
    data = reusable(request.GET.dict())
    return JsonResponse(data)


urlpatterns = [
    url(r'^account-kit/validate/$',
        csrf_exempt(account_kit_authenticate), name="verify"),
    url(r'^account-kit/redirect/$', SuccessView.as_view(),
        name='redirect'),
    url(r'^account-kit/redirect-view/$', redirect_uri, name='redirect_on_success')
]

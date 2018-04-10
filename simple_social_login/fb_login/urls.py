
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from django.http import JsonResponse
from . import settings
import json
from . import signals as fb_signals
from .utils import FacebookAPI
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from django.shortcuts import reverse
from django.dispatch import receiver
from django.contrib.auth import get_user_model, login
from . import settings


@receiver(fb_signals.data_from_fb_scope)
def onClientData(sender, request, **kwargs):
    User = get_user_model()
    user_data = kwargs.get('data')
    result = User.objects.filter(email=user_data['email']).first()
    if not result:
        result = settings.FB_CREATE_USER_CALLBACK(User, **user_data)
    # result.backend = 'django.contrib.auth.backends.ModelBackend'
    # login(request, result)
    pass

def create_or_update_user(request):
    data = {}
    if request.is_ajax():
        data = json.loads(request.body)
        fb_signals.data_from_fb_scope.send(
            sender=None, request=request, data=data)
    access_code = request.GET.get('access_token')
    if access_code:
        facebook = FacebookAPI()
        code = facebook.get_long_lived_access_token(
            access_code, request=request)
        return JsonResponse({'code': code})
    return JsonResponse(data)


class SuccessView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if settings.FB_URL_ON_SUCCESS == 'fb_login:redirect_on_success':
            return reverse(settings.FB_URL_ON_SUCCESS)
        return settings.FB_URL_ON_SUCCESS


def redirect_uri(request):
    return JsonResponse(request.GET.dict())


urlpatterns = [
    url(r'^validate/$', csrf_exempt(create_or_update_user),
        name='verify'),
    url(r'^redirect/$', SuccessView.as_view(), name='fb_redirect_uri'),

    url(r'^redirect-view/$', redirect_uri, name='redirect_on_success')

]

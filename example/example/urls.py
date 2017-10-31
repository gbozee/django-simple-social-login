"""simple_social_login URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.conf import settings
import json
from . import signals as fb_signals
from simple_s_login.account_kit.utils import AccountKitAPI
from simple_s_login.fb_login.utils import FacebookAPI
from simple_s_login.google_login.utils import GoogleAPI
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView


class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update(FACEBOOK_APP_ID=settings.FACEBOOK_ACCOUNT_KIT_APP_ID,
                       ACCOUNT_KIT_API_VERSION=settings.FACEBOOK_ACCOUNT_KIT_API_VERSION,
                       REDIRECT_URL=settings.FACEBOOK_ACCOUNT_KIT_REDIRECT_URL)
        return context


class GoogleView(TemplateView):
    template_name = "google.html"

    def get_context_data(self, **kwargs):
        context = super(GoogleView, self).get_context_data(**kwargs)
        context.update(GOOGLE_CLIENT_ID=settings.GOOGLE_CLIENT_ID)
        return context


def reusable(data):
    account_kit = AccountKitAPI()
    return account_kit.get_access_token(data['code'])


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


def create_or_update_google_user(request):
    data = {}
    if request.is_ajax():
        data = json.loads(request.body)
        google = GoogleAPI()
        data = google.verify_token(data['token'], request=request)
    return JsonResponse(data)


def account_kit_authenticate(request):
    data = {}
    if request.is_ajax():
        data = json.loads(request.body)
        data = reusable(data)
    return JsonResponse(data)


def redirect_uri(request):
    data = reusable(request.GET.dict())
    return JsonResponse(data)


urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^google/$', GoogleView.as_view(), name="google"),
    url(r'^facebook-login/$', csrf_exempt(create_or_update_user),
        name='facebook_notify'),
    url(r'^google-login/$', csrf_exempt(create_or_update_google_user),
        name="google_notify"),
    url(r'^account-kit-validate/$',
        csrf_exempt(account_kit_authenticate), name="account_kit_verify"),
    url(r'^hello/$', redirect_uri, name='account_kit_redirect_uri'),
    url(r'^admin/', admin.site.urls),
    url(r'^account_kit/',
        include("simple_s_login.account_kit.urls", namespace="account_kit")),
    url(r'^fb_login/', include("simple_s_login.fb_login.urls", namespace="fb_login")),
    url(r'^google_login/',
        include("simple_s_login.google_login.urls", namespace="google_login"))
]

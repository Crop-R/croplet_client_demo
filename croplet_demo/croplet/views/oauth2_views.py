import json
import datetime

import logging
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from croplet_demo import settings
from croplet_demo.croplet.models import Grant, AccessToken, RefreshToken

logger = logging.getLogger(__name__)

@login_required
def authorize(request):
    if not hasattr(request.user, 'access_token') or not request.user.access_token.is_valid():
        return redirect("{cropr_url}/oauth2/authorize/?response_type=code&client_id={client_id}".
                        format(cropr_url=settings.CROPR_URL, client_id=settings.CROPLET_API_CLIENT_ID))
    return redirect(reverse("home"))


def callback(request):
    error = request.GET.get('error')
    auth_code = request.GET.get('code')
    if error is not None:
        pass
    if auth_code:
        user = request.user
        if not user.is_authenticated():
            user = User.objects.create_user(username=auth_code)
        Grant.objects.update_or_create(user=user, defaults={'grant': auth_code})
        get_access_token(user)
    return redirect(reverse('home'))


def get_access_token(user):
    """
    :param user: get access token for this user
    :return: the acquired access token or None if something went wrong
    """
    assert hasattr(user, 'grant'), "user must have a grant to request an access token"
    # post authorization_code to get access token
    response = requests.post('{cropr_url}/oauth2/token/'.format(cropr_url=settings.CROPR_URL),
                             {
                                 'grant_type': 'authorization_code',
                                 'code': user.grant.grant,
                                 'client_id': settings.CROPLET_API_CLIENT_ID,
                                 'client_secret': settings.CROPLET_SECRET_API_KEY,
                                 'redirect_uri': 'http://127.0.0.2:8000/callback/'
                             }
                             )
    # grant can be deleted cause it was used (either successfully or not)
    Grant.objects.filter(user=user).delete()
    if response.status_code == 200:
        response_json = json.loads(response.text)
        _store_refresh_token(response_json, user)
        return _store_access_token(response_json, user)


def refresh_access_token(user):
    """
    :param user: refresh access token for this user
    :return: the acquired access token or None if something went wrong
    """
    assert hasattr(user, 'refresh_token'), "user must have a refresh token to get a new access token"
    # post refresh_token to get new access token
    response = requests.post('{cropr_url}/oauth2/token/'.format(cropr_url=settings.CROPR_URL),
                             {
                                 'grant_type': 'refresh_token',
                                 'refresh_token': user.refresh_token.refresh_token,
                                 'client_id': settings.CROPLET_API_CLIENT_ID,
                                 'client_secret': settings.CROPLET_SECRET_API_KEY
                             }
                             )
    if response.status_code == 200:
        response_json = json.loads(response.text)
        _store_refresh_token(response_json, user)
        return _store_access_token(response_json, user)


def _store_access_token(response_json, user):
    access_token = response_json.get('access_token')
    if access_token:
        expire_seconds = response_json.get('expires_in')
        expires = datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
        AccessToken.objects.update_or_create(user=user, defaults={'access_token': access_token, 'expires': expires})
    return access_token


def _store_refresh_token(response_json, user):
    refresh_token = response_json.get('refresh_token')
    if refresh_token:
        RefreshToken.objects.update_or_create(user=user, defaults={'refresh_token': refresh_token})

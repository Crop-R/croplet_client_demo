from django.views import generic
from croplet_demo import settings
from croplet_demo.croplet.models import Grant
from models import AccessToken
from mixins import LoggedInMixin
from urllib2 import urlopen, Request, HTTPError
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
import requests
import json
import re
import shapely.wkt


@login_required
def authorize(request):
    if hasattr(request.user, 'grant'):
        _get_access_token(request.user, request.user.grant)
    if not hasattr(request.user, 'access_token'):
        return redirect("{cropr_url}/oauth2/authorize/?response_type=code&client_id={client_id}".
                        format(cropr_url=settings.CROPR_URL, client_id=settings.CROPLET_API_CLIENT_ID))
    return redirect(reverse("map"))


class Home(generic.TemplateView):
    template_name = "croplet/base.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['topbar'] = 'home'
        return context

class MapView(LoggedInMixin, generic.TemplateView):
    template_name = "croplet/map.html"

    def get_centroid_for_field(self, client_id, field_id):
        if self.request.user.access_token:
            req = Request('{cropr_url}/api/v3/cropfield/%s/centroid?client_id={client_id}'
                          .format(cropr_url=settings.CROPR_URL, client_id=client_id))
            req.add_header('Authorization', 'Bearer %s' % self.request.user.access_token.access_token)
            req.add_header('Accept', 'application/json')
            response = urlopen(req)
            return json.loads(response.read())

    def get_data_from_gps(self, lattitude ,longitude):
        raw = requests.get('http://gps.buienradar.nl/getrr.php?lat=%s&lon=%s' % (lattitude, longitude))
        m = re.findall('\d+\|\d+\:\d+', raw.content)
        returnvalues = []
        for result in m:
            data,time = result.split('|')
            returnvalues.append({"time":time,
                                 "data": 10**((int(data)-109)/32.0)})
        return returnvalues


    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)
        client_id = settings.CROPLET_API_CLIENT_ID
        response = {}
        if(hasattr(self.request.user, "access_token")):
            token = self.request.user.access_token.access_token
        else:
            token = ''
        if token:
            req = Request('{cropr_url}/api/v3/cropfield/?client_id={client_id}'
                          .format(cropr_url=settings.CROPR_URL, client_id=client_id))
            req.add_header('Authorization', 'Bearer %s' % token)
            req.add_header('Accept', 'application/json')
            try:
                response = urlopen(req)
                response = json.loads(response.read())
                data = []
                for cropfield in response:
                    srid, polygon_wkt = cropfield.get('geometry').split(';')
                    g1 = shapely.wkt.loads(polygon_wkt)
                    bounds = list(g1.exterior.coords)
                    cropfield['centroid'] = {'x': g1.centroid.x, 'y': g1.centroid.y}
                    cropfield['rainfall'] = self.get_data_from_gps(g1.centroid.y, g1.centroid.x)
                    data.append(cropfield)
                context['cropfields'] = data
            except HTTPError as e:
                context['error'] = e
                response = e
        context['topbar'] = 'map'
        context['response'] = response
        return context

@login_required
def callback(request):

    error = request.GET.get('error')
    auth_code = request.GET.get('code')
    if(error != None):
        pass
    elif(auth_code != None):
        Grant.objects.update_or_create(
            user=request.user,
            defaults={
                'grant': auth_code
            }
        )
        _get_access_token(request.user, auth_code)
    return redirect(reverse('map'))


def _get_access_token(user, auth_code):
    client_id = settings.CROPLET_API_CLIENT_ID
    client_secret = settings.CROPLET_SECRET_API_KEY

    post_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:8005/callback/'
    }
    response = requests.post('{cropr_url}/oauth2/token/'.format(cropr_url=settings.CROPR_URL), post_data)
    if response.status_code != 200:
        Grant.objects.filter(user=user).delete()
    response = json.loads(response.text)

    if (hasattr(user, "access_token")):
        AccessToken.objects.filter(user=user).delete()
    token = AccessToken(user=user)
    access_token = response.get('access_token')
    if access_token:
        accessToken = AccessToken(user=user, access_token=access_token)
        accessToken.save()
        user.access_token = token
        user.save()


def convert_response_to_json(response):
    return json.loads(response.read())
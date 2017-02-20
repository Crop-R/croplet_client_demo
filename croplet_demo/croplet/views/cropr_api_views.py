import json
import re
from urllib2 import urlopen, Request, HTTPError

import logging
import requests
import shapely.wkt
from django.views.generic import TemplateView

from croplet_demo import settings
from croplet_demo.croplet.models import AccessToken
from croplet_demo.croplet.views.oauth2_views import refresh_access_token

logger = logging.getLogger(__name__)


class Home(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['topbar'] = 'home'
        try:
            context['farms_api_url'] = '{cropr_url}/api/v3/farms/'.format(cropr_url=settings.CROPR_URL)
            context['farms'] = call_api('farms/', self.request.user)
        except AccessToken.DoesNotExist:
            pass
        return context


class MapView(TemplateView):
    template_name = "croplet/map.html"

    def get_data_from_gps(self, lattitude, longitude):
        raw = requests.get('http://gps.buienradar.nl/getrr.php?lat=%s&lon=%s' % (lattitude, longitude))
        m = re.findall('\d+\|\d+\:\d+', raw.content)
        returnvalues = []
        for result in m:
            data, time = result.split('|')
            returnvalues.append({"time": time,
                                 "data": 10 ** ((int(data) - 109) / 32.0)})
        return returnvalues

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)
        response = {}
        if hasattr(self.request.user, "access_token"):
            token = self.request.user.access_token.access_token
        else:
            token = ''
        if token:
            req = Request('{cropr_url}/api/v3/cropfield/'.format(cropr_url=settings.CROPR_URL))
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


def call_api(endpoint, user):
    if hasattr(user, 'access_token'):
        api_url = '{cropr_url}/api/v3/{endpoint}'.format(cropr_url=settings.CROPR_URL, endpoint=endpoint)
        token = user.access_token.access_token
        try:
            return __call_api(api_url, token)
        except HTTPError as e:
            if hasattr(user, 'refresh_token'):
               return call_api(api_url, refresh_access_token(user))
            else:
                logger.exception("error requesting API: '{}' (token='{}')".format(api_url, token))


def __call_api(api_url, token):
    api_request = Request(api_url)
    api_request.add_header('Authorization', 'Bearer {}'.format(token))
    api_request.add_header('Accept', 'application/json')
    response = urlopen(api_request)
    return json.loads(response.read())

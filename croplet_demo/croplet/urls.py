from django.conf.urls import url
from django.contrib.auth import views as auth_views

from croplet_demo.croplet.views.oauth2_views import authorize, callback
from views.cropr_api_views import Home, MapView

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),

    url(r'^$', Home.as_view(), name="home"),
    url(r'map/$', MapView.as_view(), name="map"),
    url(r'authorize/$', authorize, name="authorize"),
    url(r'callback/$', callback, name="callback"),
]
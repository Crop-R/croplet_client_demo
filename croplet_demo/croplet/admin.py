from django.contrib import admin

from croplet_demo.croplet.models import AccessToken, RefreshToken

admin.site.register(AccessToken)
admin.site.register(RefreshToken)

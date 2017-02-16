from django.utils import timezone

from django.db import models


class Grant(models.Model):
    user = models.OneToOneField('auth.User', related_name='grant')
    grant = models.CharField(max_length=100)


class AccessToken(models.Model):
    user = models.OneToOneField('auth.User', related_name='access_token')
    access_token = models.CharField(max_length=100)
    expires = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.expires > timezone.now()


class RefreshToken(models.Model):
    user = models.OneToOneField('auth.User', related_name='refresh_token')
    refresh_token = models.CharField(max_length=100)

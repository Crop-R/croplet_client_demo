"""
Django settings for tutorial3 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '21234JBasdfadfasdf232342kbnaASAHVVVZZzzzzzccRYhSsqw3tHGr'

CROPLET_API_CLIENT_ID = '2DNe9SymZm6O0ukPYMAPXZr3bUsKPqepayaiFr8r' # VERVANG DIT MET UW EIGEN CLIENT ID
CROPLET_SECRET_API_KEY = 'nAbq4X5fVFW1SV3JG5DzkDaZJl2YzImISCetTPez12m4NCc4CdmBUfLeJuvIjUXahpxnxwSOFqXKa2aMvkYi3iQfFwAw5oXmi6gmIa2yrpHKvT1yefgE9EIqhSyrQVC5' # VERVANG DIT MET UW EIGEN CLIENT SECRET
CROPR_URL = 'http://localhost:8000'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['http://localhost:8000']

STATIC_URL = '/static/'
STATICFILES_DIRS = ( os.path.join(BASE_DIR, "/"), )

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'croplet_demo.croplet'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'croplet_demo/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
            ],
            'libraries': {
                'admin.urls': 'django.contrib.admin.templatetags.admin_urls',
            },
        }
    },
]



ROOT_URLCONF = 'croplet_demo.urls'

WSGI_APPLICATION = 'croplet_demo.wsgi.application'

SESSION_COOKIE_NAME = 'croplet'
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, '/media')
MEDIA_URL = '/media/'

try:
    from local_settings import *
except ImportError:
    raise Exception("Please copy local_settings_example.py to local_settings.py: `cp croplet_demo/local_settings_example.py croplet_demo/local_settings.py`")

print 'CROPLET_API_CLIENT_ID= {}'.format(CROPLET_API_CLIENT_ID)
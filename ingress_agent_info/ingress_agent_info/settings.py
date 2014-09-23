"""
Django settings for ingress_agent_info project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
import local_settings


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

TEMPLATE_DEBUG = local_settings.TEMPLATE_DEBUG

ALLOWED_HOSTS = []
ALLOWED_HOSTS.extend(local_settings.ALLOWED_HOSTS)


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis', 
    'sekizai', 
    'social.apps.django_app.default', 
    'agent', 
    'locations', 
    'user_profile', 
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', 
    'user_profile.auth_handler.GPlusAuthBackend', 
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n', 
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz', 
    'django.core.context_processors.request', 
    'django.contrib.messages.context_processors.messages', 
    'sekizai.context_processors.sekizai', 
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

ROOT_URLCONF = 'ingress_agent_info.urls'

WSGI_APPLICATION = 'ingress_agent_info.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DATABASES.update(local_settings.DATABASES)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter':'simple', 
        },
    },
    'loggers': {
        'custom': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

if getattr(local_settings, 'TIME_ZONE', None) is not None:
    TIME_ZONE = local_settings.TIME_ZONE
else:
    TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'), 
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

STATIC_URL = '/static/'

GOOGLE_OAUTH_KEY = local_settings.GOOGLE_OAUTH_KEY
GOOGLE_OAUTH_SECRET = local_settings.GOOGLE_OAUTH_SECRET

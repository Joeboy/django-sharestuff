# Settings for goingspare project. This file imports from localsettings,
# so you can (and probably should) override the defaults by creating a
# localsettings.py file.

import os
PROJECT_DIR = os.path.dirname(__file__)

LOCAL_DEV = 'TERM' in os.environ.keys()
DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'goingspare',
        'USER': 'goingspare',
        'PASSWORD': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media-admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u#sz&fkue01fmwzef-6-_4rlg=7k4$kxu$g5hataa2b!y6py(r'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
#    "django.core.context_processors.debug",
#    "django.core.context_processors.i18n",
#    "django.core.context_processors.media",
    'django.core.context_processors.request',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'goingspare.urls'

TEMPLATE_DIRS = (os.path.join(PROJECT_DIR, 'templates/'), )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.gis',
    'registration',
    'goingspare.offers',
    'goingspare.email_lists',
    'goingspare.userprofile',
    'goingspare.utils',
    'goingspare.notifications',
    'goingspare.saved',
    'goingspare.oauth',
    'sentry',
    'sentry.client',
    'taggit',
    'taggit_templatetags',
    'geo',
    'djcelery',
)

AUTH_PROFILE_MODULE = 'userprofile.UserProfile'

LOGIN_URL = '/user/login/'

LOGIN_REDIRECT_URL = '/'

ACCOUNT_ACTIVATION_DAYS = 7

GEOIP_PATH = os.path.join(PROJECT_DIR, 'geo')

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

SITE_DOMAIN = 'localhost:8000'

try:
    from localsettings import *
except ImportError:
    pass

try:
    import djcelery
    djcelery.setup_loader()
except ImportError:
    pass


# -*- coding: utf-8 -*-
# Django settings for private beta project.

import os.path
import posixpath
import pinax

from django.conf import settings
from django.views.generic.simple import direct_to_template

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
import deploy_local as deploy_config

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

# following should be set to False for prod
DEBUG = True
# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = DEBUG
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Gerald McCollam', 'gmccollam@gmail.com'),
)

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

DATABASE_ENGINE     = deploy_config.DATABASE_ENGINE
DATABASE_NAME       = deploy_config.DATABASE_NAME
DATABASE_USER       = deploy_config.DATABASE_USER
DATABASE_PASSWORD   = deploy_config.DATABASE_PASSWORD
DATABASE_HOST       = deploy_config.DATABASE_HOST
DATABASE_PORT       = deploy_config.DATABASE_PORT


FLICKR_API_KEY      = deploy_config.FLICKR_API_KEY
FLICKR_API_SECRET   = deploy_config.FLICKR_API_SECRET
FLICKR_AUTH_TOKEN   = deploy_config.FLICKR_AUTH_TOKEN
FLICKR_USER_ID      = deploy_config.FLICKR_USER_ID
FLICKR_USERNAME     = deploy_config.FLICKR_USERNAME
FLICKR_GROUP_ID     = deploy_config.FLICKR_GROUP_ID

GOOGLE_API_KEY      = deploy_config.GOOGLE_API_KEY

YOUTUBE_USERNAME     = deploy_config.YOUTUBE_USERNAME

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/media/'

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/site_media/static/'

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('greenline', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0+27w@lerk7-5)s^t9y!e#k6!+zqojlinw37^l=d10ygaldq$='

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'greenline.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "pinax.core.context_processors.pinax_settings",
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.openid",
    "account.context_processors.account",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.admin',
    'pinax.templatetags',
        
    # external
    'notification', # must be first
    'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    'friends',
    'mailer',
    'messages',
    'announcements',
    'oembed',
    'pagination',
    'gravatar',
    'timezones',
    'bookmarks',
    'threadedcomments',
    'threadedcomments_extras',
    'voting',
    'voting_extras',
    #'tagging',
    'ajax_validation',
    'avatar',
    'flag',
    'uni_form',
    'django_sorting',
    'django_markup',
    'staticfiles',
    'debug_toolbar',

    'analytics',
    'profiles',
    'account',
    
    'django.contrib.admin',
    
    # specific to our app
    'ideas',
    'photos',
    'videos',
    'principles',
    'location',
    'sharing',
    'stations',
    'taggit',
)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

COMMENTS_APP = 'threadedcomments'

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'cloak_email_addresses': True,
    'file_insertion_enabled': False,
    'raw_enabled': False,
    'warning_stream': NullStream(),
    'strip_comments': True,
}

AUTH_PROFILE_MODULE = 'basic_profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
DEFAULT_FROM_EMAIL = "interactivesomerville@gmail.com"
CONTACT_EMAIL = "interactivesomerville@gmail.com"
ACTIVE_SITE = "interactive-beta.org"
#ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

if ACCOUNT_OPEN_SIGNUP:
    signup_view = "account.views.signup"
else:
    signup_view = "signup_codes.views.signup"
    
SITE_NAME = "Interactive Somerville"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = None
LOGIN_REDIRECT_URL = "/"

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

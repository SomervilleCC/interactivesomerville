import os

DATABASE_ENGINE = 'django.contrib.gis.db.backends.postgis'
DATABASE_NAME = 'greenline'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = ''  # supply your postgres password
DATABASE_HOST = ''
DATABASE_PORT = ''

DEBUG = True

SECRET_KEY = ''

# this key should be good for interactive-beta.org. used for geocoding
GOOGLE_API_KEY = 'ABQIAAAANeuGqCBLzo8ye_8Sw_AOpBTpH3CbXHjuCVmaTc5MkkU4wO1RRhQs0hLhAs4oSlSyDPIGQel8EIyrmg'
YAHOO_APP_ID = '4BRX3JfV34E7uaK02MDR.5nn7EAw7DptfhbRTdrMQQjHbXVedgXfsQLaFWwp7fIm'

DISQUS_API_KEY = 'ZymM2jx505ECV2yj9QT1GH5QCc6aMhfkN1vjR8wF8WQnOQxg8IYx8ppGzxljxkcr'
DISQUS_WEBSITE_SHORTNAME = 'scc-test'

# This key is for the YouTube Data API. See http://code.google.com/apis/youtube/faq.html#functionality 
GOOGLE_UT_DATA_API_KEY = 'AI39si7l2sXtQVqqiYolj6faLXu6VnDjbUX70Vnh8AmcB838sKPlxFNvWdPqb5D8VCzi42AKVD0ufBigUN3-aV_1c8FDjiYLUQ'

YOUTUBE_USERNAME = 'intersomerville'

AKISMET_API_KEY = ''

GOOGLE_ANALYTICS_KEY = ''

ACCOUNT_ACTIVATION_DAYS = ''

FLICKR_HOST = 'http://flickr.com'

FLICKR_API = '/services/rest'

FLICKR_API_KEY = '464e5ea966ce1a545a82a089813b81a2'
FLICKR_API_SECRET = '7a540df8f702b903'
FLICKR_AUTH_TOKEN = '72157624177675436-db6d5243cf94f9bc'

# interactivesomerville, the user
FLICKR_USER_ID = '47846239@N04'
#FLICKR_USER_ID = '55762072@N00'
FLICKR_USERNAME = 'interactivesomerville'
FLICKR_API_KEY = '464e5ea966ce1a545a82a089813b81a2'
FLICKR_API_SECRET = '7a540df8f702b903'
FLICKR_AUTH_TOKEN = '72157624177675436-db6d5243cf94f9bc'

# somerville_community, the group
FLICKR_GROUP_ID = '1341011@N20'

# interactivesomerville, the group
FLICKR_GROUP_ID = '1341011@N20'

FLICKR_TAGS_PREFIX = ''

FLICKR_UPLOAD_DIR = ''

FLICKR_TEST_FILE = 'data_model.png'

ROOT_URLCONF = 'greenline.urls'

CONTACT_EMAIL = ""

SITE_NAME = "greenline"

STATIC_URL = '/site_media/static/'


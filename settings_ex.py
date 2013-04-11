# example settings for this project
# overwrites static settings in settings.py

from settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
        ('Stephen Trusheim', 'tru+waivers@sse.stanford.edu'),
)

MANAGERS = ADMINS

STATIC_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':   '',                      # Or path to database file if using sqlite3.
        'USER':   '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'America/Los_Angeles'

MEDIA_ROOT = '/Users/stephen/Desktop/waivers/media/'
TEMPLATE_DIRS = ('/Users/stephen/Desktop/waivers/templates',)
BASE_URL = 'http://localhost:8000/'

SECRET_KEY = '4jd607m#-)re#asdasgasdfgakd7zj9**7o_+3%=v4)h9523+%1o$a3_fm2yl'
WEBAUTH_SHARED_SECRET = 'test'
WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'
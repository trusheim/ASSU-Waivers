# example settings for this project
# overwrites static settings in settings.py

from settings import *

MEDIA_ROOT = '/Users/stephen/Desktop/waivers/media/'
TEMPLATE_DIRS = ('/Users/stephen/Desktop/waivers/templates',)

WEBAUTH_SHARED_SECRET = 'test'
WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'
BASE_URL = 'http://localhost:8000/'
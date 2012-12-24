from django.conf.urls.defaults import patterns

__author__ = 'trusheim'


urlpatterns = patterns('waivers_api.views',
    (r'^(?P<api_key>[\w\d-]+)/test/?$', 'test'),
    (r'^(?P<api_key>[\w\d-]+)/fees/?$', 'getFees'),
    (r'^(?P<api_key>[\w\d-]+)/terms/?$', 'getTerms'),
    (r'^(?P<api_key>[\w\d-]+)/checkFee/?$', 'checkFeeStatus'),
    (r'^(?P<api_key>[\w\d-]+)/waiverList/?$', 'getWaiversList'),

    (r'^(?P<api_key>[\w\d-]+)/viewStudent/?$', 'viewStudent'),

    (r'^.*?$', 'not_found')
)
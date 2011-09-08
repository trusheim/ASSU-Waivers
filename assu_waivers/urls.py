from django.conf.urls.defaults import *

urlpatterns = patterns('waivers.assu_waivers.views',
    (r'^$', 'index'),
    (r'^request/$', 'request')
)

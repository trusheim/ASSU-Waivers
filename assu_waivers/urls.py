from django.conf.urls.defaults import *

urlpatterns = patterns('waivers.assu_waivers.views',
    (r'^$', 'index'),
    (r'^about/$', 'about'),
    (r'^request/$', 'request'),

    # admin
    (r'^request/$', 'request')

)

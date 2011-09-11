from django.conf.urls.defaults import *

urlpatterns = patterns('waivers.assu_waivers.views',
    (r'^$', 'index'),
    (r'^about/$', 'about'),
    (r'^request/$', 'request'),

    # admin
    (r'^reports/$', 'admin_reportIndex'),
    (r'^reports/groups/(?P<termName>[\w\d-]+)/?$', 'admin_bygroupTermReport'),
    (r'^reports/students/(?P<termName>[\w\d-]+)/?$', 'admin_bystudentTermReport'),
    (r'^reports/group_public/(?P<groupId>[\d]+)/(?P<termName>[\w\d-]+)/?$', 'admin_bygroupTermListReport')


)

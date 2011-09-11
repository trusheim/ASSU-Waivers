from django.conf.urls.defaults import *

urlpatterns = patterns('waivers.assu_waivers.views',
    (r'^$', 'index'),
    (r'^about/$', 'about'),
    (r'^request/$', 'request'),

    # admin
    (r'^reports/$', 'admin_reportIndex'),
    (r'^reports/groups/(?P<termName>[\w\d-]+)/?$', 'admin_bygroupTermReport'),
    (r'^reports/students/(?P<termName>[\w\d-]+)/?$', 'admin_bystudentTermReport'),
    (r'^reports/group/(?P<termName>[\w\d-]+)/(?P<groupId>[\d]+)/?$', 'admin_bygroupTermListReport', {'public': False}, 'groupreport_private'),
    (r'^reports/group/(?P<termName>[\w\d-]+)/(?P<groupId>[\d]+)/public/?$', 'admin_bygroupTermListReport', {'public': True}, 'groupreport_public'),

    (r'^reports/export/(?P<termName>[\w\d-]+)/prn/$', 'admin_exportPrn'),
    (r'^reports/export/(?P<termName>[\w\d-]+)/csv/$', 'admin_exportCsv'),


)

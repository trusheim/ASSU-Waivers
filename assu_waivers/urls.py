from django.conf.urls.defaults import *

urlpatterns = patterns('waivers.assu_waivers',
    (r'^$', 'views.index'),
    (r'^about/$', 'views.about'),
    (r'^request/$', 'views.request'),

    # admin
    (r'^reports/$', 'admin_views.reportIndex'),
    (r'^reports/groups/(?P<termName>[\w\d-]+)/?$', 'admin_views.bygroupTermReport'),
    (r'^reports/students/(?P<termName>[\w\d-]+)/?$', 'admin_views.bystudentTermReport'),
    (r'^reports/students/(?P<termName>[\w\d-]+)/(?P<student>[\w\d-]+)/?$', 'admin_views.studentReport'),

    (r'^reports/group/(?P<termName>[\w\d-]+)/(?P<groupId>[\d]+)/?$', 'admin_views.bygroupTermListReport', {'public': False}, 'groupreport_private'),
    (r'^reports/group/(?P<termName>[\w\d-]+)/(?P<groupId>[\d]+)/public/?$', 'admin_views.bygroupTermListReport', {'public': True}, 'groupreport_public'),

    (r'^reports/export/(?P<termName>[\w\d-]+)/prn/$', 'admin_views.exportPrn'),
    (r'^reports/export/(?P<termName>[\w\d-]+)/csv/$', 'admin_views.exportCsv'),

    (r'^reports/upload/(?P<termName>[\w\d-]+)/$', 'admin_views.importStudentCsv'),



)
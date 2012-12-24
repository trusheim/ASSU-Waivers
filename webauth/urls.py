from django.conf.urls.defaults import *

urlpatterns = patterns('webauth.views',
    (r'^logout/$', 'logout'),
    (r'^login/$','login'),
    (r'^whoami$','whoami'),
    #(r'^changeme/(?P<newsunet>[\w\d-]+)','TEST_changeme'),
)
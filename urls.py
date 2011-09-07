from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()
admin.site.login_template = 'webauth/admin_redirect.html'

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
           {'document_root': 'media/'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^webauth/', include('webauth.urls')),

    (r'^', include('waivers.assu_waivers.urls')),

)

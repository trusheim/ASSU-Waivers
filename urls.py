from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()
admin.site.login_template = 'webauth/admin_redirect.html'

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
           {'document_root': settings.MEDIA_ROOT}),
    (r'^admin/', include(admin.site.urls)),
    (r'^webauth/', include('webauth.urls')),
    (r'^api/', include('waivers.waivers_api.urls')),
    (r'^', include('waivers.assu_waivers.urls')),

)

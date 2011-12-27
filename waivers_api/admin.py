from django.contrib import admin
from waivers_api.models import ApiKey, ApiPrivilege

__author__ = 'trusheim'

admin.site.register(ApiKey)
admin.site.register(ApiPrivilege)
from django.http import HttpResponse
from waivers_api.api import JsonResponse, ERRORS
from waivers_api.models import ApiPrivilege, ApiKey

__author__ = 'trusheim'

def requirePrivilege(privilege):
    def decorator(fn):
        def hasPermission(*args,**kwargs):
            if 'api_key' not in kwargs.keys():
                return JsonResponse.BadRequestError()
            key_name = kwargs['api_key']

            if nameHasPrivilege(key_name,privilege):
                return fn(*args,**kwargs)
            else:
                return JsonResponse.BadApiKeyError()
        return hasPermission
    return decorator

def nameHasPrivilege(key_name,privilege):
    try:
        api_key = ApiKey.objects.get(key=key_name)
    except ApiKey.DoesNotExist:
        return False

    if isinstance(privilege,basestring):
        return api_key.hasPrivilege(privilege)
    else:
        for name in privilege:
            if api_key.hasPrivilege(name):
                return True
        return False
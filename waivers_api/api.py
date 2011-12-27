import json
from django.http import HttpResponse, Http404

__author__ = 'trusheim'


STATUS = {
    'error': 0,
    'okay': 1,
}

ERRORS = {
    'bad_request': 404,
    'internal_error': 500,
    'bad_api': 403,
    'okay': 200,
    'no_objects': 800
}
class JsonResponse(object):
    status = STATUS['okay']
    content = dict()

    def __init__(self,content=None):
        if isinstance(content,dict):
            self.content = content
        elif isinstance(content, basestring):
            self.content = {'message': content}
        else:
            pass


    def toHttpResponse(self):
        self.content['status'] = self.status
        return HttpResponse(json.dumps(self.content,ensure_ascii=False), mimetype="application/json")


    @classmethod
    def Error(cls,code,message):
        response = cls()
        response.status = STATUS['error']
        response.content = {
            'error_code': code,
            'error_message': message
        }
        return response.toHttpResponse()

    @classmethod
    def BadRequestError(cls):
        return cls.Error(ERRORS['bad_request'],"API resource not found.")

    @classmethod
    def BadApiKeyError(cls):
        return cls.Error(ERRORS['bad_api'],"The API key was not found, is deactivated, "
                                           "or does not have permission for ther requested resource.")

    @classmethod
    def NoObjects(cls):
        return cls.Error(ERRORS['no_objects'],"Your request relies on input that does not seem to exist.")

def api(fn):
    def decorator(*args,**kwargs):
        try:
            return fn(*args,**kwargs)
        except Http404:
            return JsonResponse.NoObjects()
    return decorator
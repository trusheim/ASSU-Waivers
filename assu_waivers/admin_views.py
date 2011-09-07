from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import HttpResponse

__author__ = 'trusheim'

@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    return HttpResponse('right-o, cheerio')
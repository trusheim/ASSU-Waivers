import random
import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from assu_waivers.services import GetTermForDate

@login_required
def index(request):
    term = GetTermForDate(datetime.datetime.now())
    if term is None:
        return closed(request)
    else:
        return waiverinfo(request,term)

def closed(request):
    return render_to_response('waivers/closed.html', {}, context_instance=RequestContext(request))

def waiverinfo(request, term):
    return render_to_response('waivers/info.html', {'term': term}, context_instance=RequestContext(request))

def waiver(request):
    term = GetTermForDate(datetime.datetime.now())

    if term is None:
        return closed(request)

    # need a form
    # need to load old requests
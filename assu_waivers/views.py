import random
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from assu_waivers.forms import WaiverForm
from assu_waivers.services import GetTermForDate, GetStudentFromUser

@login_required
def index(request):
    term = GetTermForDate(datetime.now())
    if term is None:
        return closed(request)
    else:
        return waiverinfo(request,term)

def closed(request):
    return render_to_response('waivers/closed.html', {}, context_instance=RequestContext(request))

def waiverinfo(request, term):
    return render_to_response('waivers/info.html', {'term': term}, context_instance=RequestContext(request))

def error(request,message):
    return render_to_response('waivers/error.html', {'message': message}, context_instance=RequestContext(request))

def request(request):
    term = GetTermForDate(datetime.now())
    if term is None:
        return closed(request)

    student = GetStudentFromUser(request.user)
    if student is None:
        return error(request,'notstudent')
    if student.no_waiver:
        return error(request,'nowaiver')

    forms = WaiverForm.get_list(term,student)
    if request.method == 'POST':
        forms = WaiverForm.get_list(term,student,data=request.POST)
        if WaiverForm.verify_list(forms):
            WaiverForm.save_list(forms)
            return render_to_response('waivers/complete.html',{'date': datetime.now()}, context_instance=RequestContext(request))

    return render_to_response('waivers/request.html',{'forms': forms}, context_instance=RequestContext(request))
import codecs
import csv
import random
from datetime import datetime
import StringIO
from time import strftime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum, Avg
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from assu_waivers.forms import WaiverForm, StudentUploadForm
from assu_waivers.models import Fee, Term, Enrollment, FeeWaiver, Student
from assu_waivers.services import GetTermForDate, GetStudentFromUser, prnText

@login_required
def index(request):
    term = GetTermForDate(datetime.now())
    if term is None:
        return closed(request)
    else:
        return waiverinfo(request,term)

def closed(request):
    return render_to_response('waivers/closed.html', None, context_instance=RequestContext(request))

def waiverinfo(request, term):
    return render_to_response('waivers/info.html', {'term': term}, context_instance=RequestContext(request))

def error(request,message):
    return render_to_response('waivers/error.html', {'message': message}, context_instance=RequestContext(request))

def about(request):
    return render_to_response('waivers/about.html', None, context_instance=RequestContext(request))


def request(request):
    term = GetTermForDate(datetime.now())
    if term is None:
        return closed(request)

    student = GetStudentFromUser(request.user)
    if student is None:
        return error(request,'notstudent')
    if term not in student.terms.all():
        return error(request,'notstudent')
    if student.no_waiver:
        return error(request,'nowaiver')

    enrollment = Enrollment.objects.select_related().get(student=student,term=term)

    forms = WaiverForm.get_list(enrollment)
    is_error = False
    if request.method == 'POST':
        forms = WaiverForm.get_list(enrollment,data=request.POST)
        if WaiverForm.verify_list(forms):
            WaiverForm.save_list(forms)
            return render_to_response('waivers/complete.html',{'date': datetime.now(), 'term': term}, context_instance=RequestContext(request))
        else:
            is_error = True

    return render_to_response('waivers/request.html',{'forms': forms,'error':is_error}, context_instance=RequestContext(request))
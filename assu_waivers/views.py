import random
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from assu_waivers.forms import WaiverForm
from assu_waivers.models import Fee, Term, Enrollment
from assu_waivers.services import GetTermForDate, GetStudentFromUser

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
    if request.method == 'POST':
        forms = WaiverForm.get_list(enrollment,data=request.POST)
        if WaiverForm.verify_list(forms):
            WaiverForm.save_list(forms)
            return render_to_response('waivers/complete.html',{'date': datetime.now(), 'term': term}, context_instance=RequestContext(request))

    return render_to_response('waivers/request.html',{'forms': forms}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_export(request):
    return HttpResponseRedirect(reverse('django.contrib.admin.views.index'))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_groupreport(request,termName):

    total_refund = [0,0,0]
    if termName is not None:
        term = get_object_or_404(Term,short_name=termName)

        fees = Fee.objects.filter(term=term)

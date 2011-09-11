import random
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum, Avg
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from assu_waivers.forms import WaiverForm
from assu_waivers.models import Fee, Term, Enrollment, FeeWaiver
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
    is_error = False
    if request.method == 'POST':
        forms = WaiverForm.get_list(enrollment,data=request.POST)
        if WaiverForm.verify_list(forms):
            WaiverForm.save_list(forms)
            return render_to_response('waivers/complete.html',{'date': datetime.now(), 'term': term}, context_instance=RequestContext(request))
        else:
            is_error = True

    return render_to_response('waivers/request.html',{'forms': forms,'error':is_error}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_export(request):
    return HttpResponseRedirect(reverse('django.contrib.admin.views.index'))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportIndex(request):
    terms = Term.objects.all()
    return render_to_response('waivers/admin/report_index.html',{'terms': terms}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_bygroupTermReport(request,termName):

    fee_info = []
    term = get_object_or_404(Term,short_name=termName)

    fees = Fee.objects.filter(term=term)
    total_waiver = [0,0,0]
    for fee in fees:
        total = fee.feewaiver_set.aggregate(Sum('amount'))['amount__sum']
        if total is None:
            total = 0

        total_waiver[fee.population] += total

        average = fee.feewaiver_set.aggregate(Avg('amount'))['amount__avg']
        if average is None:
            average = 0

        count = fee.feewaiver_set.count()

        total_enrollment = Enrollment.objects.filter(term=fee.term,population=fee.population).count()
        if total_enrollment == 0:
            total_enrollment = 1 # hacktastical, prevent div by 0 errors

        pct = count / float(total_enrollment) * 100.0
        avg_pct = average / fee.max_amount * 100.0

        fee_info.append({'fee': fee,
                         'total': total,
                         'average': average,
                         'count': count,
                         'pct': pct,
                         'avg_pct': avg_pct
        })

    return render_to_response('waivers/admin/group_termreport.html',{
        'groups': fee_info,
        'term':term,
        'date': datetime.now(),
        'aggregate': total_waiver
    }, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_bystudentTermReport(request,termName):
    term = get_object_or_404(Term,short_name=termName)

    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk','student__sunetid').annotate(total_waiver=Sum('amount'))
    return render_to_response('waivers/admin/user_termreport.html',{'waivers': waivers,'term':term, 'date': datetime.now()}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_bygroupTermListReport(request,termName,groupId):
    term = get_object_or_404(Term,short_name=termName)
    fee = get_object_or_404(Fee,pk=groupId)

    waivers = fee.feewaiver_set.select_related().order_by('student__suid').all()

    total_waiver = fee.feewaiver_set.aggregate(Sum('amount'))['amount__sum']
    if total_waiver is None:
        total_waiver = 0

    return render_to_response('waivers/admin/group_termlistreport.html',{
        'fee': fee,
        'waivers': waivers,
        'total_waiver': total_waiver,
        'term':term,
        'date': datetime.now()
    }, context_instance=RequestContext(request))
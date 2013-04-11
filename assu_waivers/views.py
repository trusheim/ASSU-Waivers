from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Sum
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from assu_waivers.forms import WaiverForm
from assu_waivers.models import Fee, Enrollment, FeeWaiver
from assu_waivers.services import GetTermForDate, GetStudentFromUser


@login_required
def index(request):
    term = GetTermForDate(datetime.now())
    if term is None:
        return closed(request)
    else:
        return waiverinfo(request, term)


def closed(request):
    return render_to_response('waivers/closed.html', None, context_instance=RequestContext(request))


def waiverinfo(request, term):
    return render_to_response('waivers/info.html', {'term': term}, context_instance=RequestContext(request))


def error(request, message):
    return render_to_response('waivers/error.html', {'message': message}, context_instance=RequestContext(request))


def about(request):
    return render_to_response('waivers/about.html', None, context_instance=RequestContext(request))


@login_required
def request(request):
    term = GetTermForDate(datetime.now())
    if term is None:
        return closed(request)

    student = GetStudentFromUser(request.user)
    if student is None:
        return error(request, 'notstudent')
    if term not in student.terms.all():
        return error(request, 'notstudent')
    if student.no_waiver:
        return error(request, 'nowaiver')

    enrollment = Enrollment.objects.select_related().get(student=student, term=term)

    forms = WaiverForm.get_list(enrollment)
    is_error = False
    if request.method == 'POST':
        forms = WaiverForm.get_list(enrollment, data=request.POST)
        if WaiverForm.verify_list(forms):
            WaiverForm.save_list(forms)

            # logic to determine total amount of waivers, total possible amount
            possible = Fee.objects.filter(term=term, population=enrollment.population).aggregate(Sum('max_amount'))[
                'max_amount__sum']
            total = FeeWaiver.objects.filter(fee__term=term, student=student).aggregate(Sum('amount'))['amount__sum']

            if possible is None:
                possible = 0
            if total is None:
                total = 0

            return render_to_response('waivers/complete.html',
                                      {'date': datetime.now(),
                                       'term': term,
                                       'total': total,
                                       'possible': possible,
                                       'population': enrollment.get_population_display()
                                      }, context_instance=RequestContext(request))
        else:
            is_error = True

    return render_to_response('waivers/request.html', {'forms': forms, 'error': is_error},
                              context_instance=RequestContext(request))
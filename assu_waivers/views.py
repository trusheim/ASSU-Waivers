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

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reportIndex(request):
    terms = Term.objects.order_by('-pk').all()
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

    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk','student__sunetid','student__name').annotate(total_waiver=Sum('amount'))
    return render_to_response('waivers/admin/user_termreport.html',{'waivers': waivers,'term':term, 'date': datetime.now()}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_bygroupTermListReport(request,termName,groupId,public=False):
    term = get_object_or_404(Term,short_name=termName)
    fee = get_object_or_404(Fee,pk=groupId)

    waivers = fee.feewaiver_set.select_related().order_by('student__suid').all()

    total_waiver = fee.feewaiver_set.aggregate(Sum('amount'))['amount__sum']
    if total_waiver is None:
        total_waiver = 0

    if public:
        template = 'waivers/admin/group_termlistreport_public.html'
    else:
        template = 'waivers/admin/group_termlistreport.html'

    return render_to_response(template,{
        'fee': fee,
        'waivers': waivers,
        'total_waiver': total_waiver,
        'term':term,
        'date': datetime.now()
    }, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_exportPrn(request,termName):
    """
    PRN is just space-delimited text (i.e., there is a field width, and we either truncate or pad with spaces until we are that length.)
    File format, per the SSC on Sep 1 2011:
    No header column
    File must be left justified
    Amount Format	2 decimal places, no comma separator
    A	Emplid	[ST: SUID] column width 10
    B	Name	column width 32
    C	Item Type [ST: ????]	column width 15
    D	Amount	column width 10
    E	Term	column width 5
    F	Reference (optional)	column width 15
    Total Number of Records
    Total Amount
    """
    term = get_object_or_404(Term,short_name=termName)

    output = cStringIO.StringIO()

    total_waiver = 0
    num_reqs = 0
    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk','student__sunetid','student__name','updated').annotate(total_amount=Sum('amount'))

    # each waiver: requested values
    for waiver in waivers:
        num_reqs += 1
        amount_text = "%.2f" % waiver['total_amount']
        total_waiver += waiver['total_amount']
        datetime_text = waiver['updated'].strftime("%y-%m-%d-%H-%M")

        output.write(prnText(waiver['student__pk'],10))
        output.write(prnText(waiver['student__name'],32))
        output.write(prnText("700000000001",15))
        output.write(prnText(amount_text,10))
        output.write(prnText(term.short_name,5))
        output.write(prnText(datetime_text,15))
        output.write("\n")

    # end line: number of records and total amount
    output.write(prnText(str(num_reqs),10))
    output.write(prnText('',32))
    output.write(prnText('',15))
    output.write(prnText("%.2f" % total_waiver,10))
    output.write(prnText('',5))
    output.write(prnText('',15))

    final = output.getvalue()
    output.close()

    filename =  "%s_ASSU_WAIVERS_%s.dat" % (strftime("%Y_%m_%d"), str(term.short_name).upper())

    #response = HttpResponse()
    response = HttpResponse(mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response.write(final)

    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_exportCsv(request,termName):
    term = get_object_or_404(Term,short_name=termName)

    output = StringIO.StringIO()
    obuffer = codecs.getwriter("utf-8")(output)
    output_csv = csv.writer(obuffer)

    total_waiver = 0
    num_reqs = 0
    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk','student__sunetid','student__name','updated').annotate(total_amount=Sum('amount'))

    output_csv.writerow([unicode('SUID'),unicode('Name'),unicode('Type'),
                         unicode('Total Waiver'),unicode('Term'),unicode('Reference Date')])

    for waiver in waivers:
        num_reqs += 1
        amount_text = "%.2f" % waiver['total_amount']
        total_waiver += waiver['total_amount']
        datetime_text = waiver['updated'].strftime("%y-%m-%d-%H-%M")

        output_csv.writerow([
            waiver['student__pk'],
            waiver['student__name'].encode('ascii','ignore'),
            '700000000001',
            amount_text,
            term.short_name,
            datetime_text
            ])

    final = output.getvalue()
    output.close()

    filename =  "%s_ASSU_WAIVERS_%s.csv" % (strftime("%Y_%m_%d"), str(term.short_name).upper())

    #response = HttpResponse()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response.write(final)

    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_importStudentCsv(request, termName):
    """
    Student CSV format: SUID, Name, SUNetID, Bill Category
        - Bill Category: UG, GR, [GSB, MED, LAW] (all considered GR)
        - WILL NEED TO BE CHANGED FOR WINTER QUARTER
    Athletic people CSV format: sport, name, SUID
        - Sport and name are discarded
    """
    term = get_object_or_404(Term,short_name=termName)

    form = StudentUploadForm()
    if request.method == 'POST':
        form = StudentUploadForm(request.POST,request.FILES)

    if not form.is_valid():
        return render_to_response('waivers/admin/upload.html',{'form': form,'term': term}, context_instance=RequestContext(request))

    # process NCAA exemptions
    try:
        athlete_csv = request.FILES['athletes']
        lines = []
        for chunk in athlete_csv.chunks():
            lines += chunk.splitlines()
        reader = csv.reader(lines)

        num_exceptions = 0

        exceptions = set()
        for student in reader:
            exceptions.add(student[2])
            num_exceptions += 1
    except Exception as e:
       return render_to_response('waivers/admin/upload_done.html',{'error': e}, context_instance=RequestContext(request))

    try:

        csv_file = request.FILES['csv']
        lines = []
        for chunk in csv_file.chunks():
            lines += chunk.splitlines()

        reader = csv.reader(lines)
        num_updated = 0

        for student_record in reader:
            no_waivers = False
            if student_record[0] in exceptions:
                no_waivers = True
            student = Student.objects.get_or_create(suid=student_record[0],
                                                    defaults={'sunetid': student_record[2].lower(), 'name': "UNKNOWN",'no_waiver': no_waivers})
            student = student[0]
            student.name = unicode(student_record[1],'utf-8')
            student.no_waiver = no_waivers
            student.save()

            enrollment = Enrollment.objects.get_or_create(student=student, term=term, defaults={'population': Student.popFromRegistrarStatus(student_record[3])})
            num_updated += 1

        return render_to_response('waivers/admin/upload_done.html',{'num': num_updated, 'term': term}, context_instance=RequestContext(request))
    except Exception as e:
        return render_to_response('waivers/admin/upload_done.html',{'error': e}, context_instance=RequestContext(request))



import StringIO
import codecs
import csv
from datetime import datetime
from time import strftime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.aggregates import Sum, Avg
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from assu_waivers.forms import StudentUploadForm
from assu_waivers.models import Term, Fee, Enrollment, FeeWaiver, Student
from assu_waivers.services import prnText

@login_required
@user_passes_test(lambda u: u.is_staff)
def reportIndex(request):
    terms = Term.objects.order_by('-pk').all()
    return render_to_response('waivers/admin/report_index.html',{'terms': terms}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def bygroupTermReport(request,termName):

    fee_info = []
    term = get_object_or_404(Term,short_name=termName)

    fees = Fee.objects.filter(term=term)
    total_waiver = [0,0] # removing Law
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

    num_waivers = [0,0]
    num_waivers[0] = FeeWaiver.objects.filter(fee__term=term,fee__population=0).values('student__pk','student__sunetid','student__name').distinct().count()
    num_waivers[1] = FeeWaiver.objects.filter(fee__term=term,fee__population=1).values('student__pk','student__sunetid','student__name').distinct().count()


    return render_to_response('waivers/admin/group_termreport.html',{
        'groups': fee_info,
        'term':term,
        'date': datetime.now(),
        'aggregate': total_waiver,
        'num': num_waivers
    }, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def bystudentTermReport(request,termName):
    term = get_object_or_404(Term,short_name=termName)

    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk','student__sunetid','student__name').annotate(total_waiver=Sum('amount'))
    return render_to_response('waivers/admin/user_termreport.html',{'waivers': waivers,'term':term, 'date': datetime.now()}, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def studentReport(request,termName,student):
    term = get_object_or_404(Term,short_name=termName)
    student = get_object_or_404(Student,sunetid=student)
    enrollment = get_object_or_404(Enrollment,student=student,term=term)
    population = enrollment.get_population_display()

    waivers = FeeWaiver.objects.filter(fee__term=term,student=student)
    possible_waivers = Fee.objects.filter(term=term,population=enrollment.population)

    not_waived = set(possible_waivers)
    total = 0
    for waiver in waivers:
        not_waived.remove(waiver.fee)
        total += waiver.amount

    possible = Fee.objects.filter(term=term,population=enrollment.population).aggregate(Sum('max_amount'))['max_amount__sum']
    if possible is None:
        possible = 0

    return render_to_response('waivers/admin/user_termreportone.html',
        {
            'waivers': waivers,
            'term':term,
            'student': student,
            'date': datetime.now(),
            'not_waived':not_waived,
            'total': total,
            'possible': possible,
            'enrollment': population
        }, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_staff)
def bygroupTermListReport(request,termName,groupId,public=False):
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
def exportPrn(request,termName):
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

    output = StringIO.StringIO()
    obuffer = codecs.getwriter("utf-8")(output)

    total_waiver = 0
    num_reqs = 0
    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk','student__sunetid','student__name','updated').annotate(total_amount=Sum('amount'))

    # each waiver: requested values
    for waiver in waivers:
        num_reqs += 1
        amount_text = "%.2f" % waiver['total_amount']
        total_waiver += waiver['total_amount']
        datetime_text = waiver['updated'].strftime("%y-%m-%d-%H-%M")

        obuffer.write(prnText(waiver['student__pk'],10))
        obuffer.write(prnText(waiver['student__name'].encode('ascii','replace'),32))
        obuffer.write(prnText("700000000001",15))
        obuffer.write(prnText(amount_text,10))
        obuffer.write(prnText(term.short_name,5))
        obuffer.write(prnText(datetime_text,15))
        obuffer.write("\n")

    # end line: number of records and total amount
    obuffer.write(prnText(str(num_reqs),10))
    obuffer.write(prnText('',32))
    obuffer.write(prnText('',15))
    obuffer.write(prnText("%.2f" % total_waiver,10))
    obuffer.write(prnText('',5))
    obuffer.write(prnText('',15))

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
def exportCsv(request,termName):
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
            waiver['student__name'].encode('ascii','replace'),
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
def importStudentCsv(request, termName):
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



from django.db.models import Sum, Avg
from assu_waivers.models import Term, Student, Enrollment, FeeWaiver, Fee


def GetTermForDate(datetime):
    try:
        term = Term.objects.filter(refund_opens__lte=datetime, refund_closes__gte=datetime).get()
        return term
    except Term.DoesNotExist:
        return None
    except Term.MultipleObjectsReturned:
        raise Exception("Multiple terms overlap on " + str(datetime) + ". Failure.")


def GetStudentFromUser(user):
    sunetid = user.username
    try:
        student = Student.objects.get(sunetid=sunetid)
        return student
    except Student.DoesNotExist:
        return None
    except Student.MultipleObjectsReturned:
        raise Exception("Multiple students with SUNetID " + sunetid)


def SunetPaidFee(sunetid, fee):
    try:
        student = Student.objects.get(sunetid=sunetid)
    except Student.DoesNotExist:
        return False, 'not_found', "SUID not found in database"

    return StudentPaidFee(student, fee)


def StudentPaidFee(student, fee):
    try:
        enrollment = Enrollment.objects.get(term=fee.term, student=student)
    except Enrollment.DoesNotExist:
        return False, 'not_enrolled', "Student was not listed as enrolled during the fee's term"

    try:
        waiver = FeeWaiver.objects.get(fee=fee, student=student)
    except FeeWaiver.DoesNotExist:
        return True, 'paid', "Student paid the fee and did not waive it."

    return False, 'waived', "Student waived fee with reason: '%s'" % waiver.reason


def getTermStatistics(term):
    stats = {}

    fees = Fee.objects.filter(term=term)
    total_waiver = [0, 0]
    total_fee = [0, 0]
    avg_category_pct = [0.0, 0.0]
    category_count = [0.000001, 0.000001]  # div by 0 errors

    stats['enrollment_ug'] = Enrollment.objects.filter(term=term, population=0).count()
    stats['enrollment_grad'] = Enrollment.objects.filter(term=term, population=1).count()
    if stats['enrollment_ug'] == 0:
        stats['enrollment_ug'] = 1 # div by zero error fix
    if stats['enrollment_grad'] == 0:
        stats['enrollment_grad'] = 1 # div by zero error fix

    fee_info = []

    for fee in fees:

        total_fee[fee.population] += fee.max_amount

        total = fee.feewaiver_set.aggregate(Sum('amount'))['amount__sum']
        if total is None:
            total = 0

        total_waiver[fee.population] += total

        average = fee.feewaiver_set.aggregate(Avg('amount'))['amount__avg']
        if average is None:
            average = 0

        count = fee.feewaiver_set.count()

        if fee.population == 0:
            pct = count / float(stats['enrollment_ug']) * 100.0
        else:
            pct = count / float(stats['enrollment_grad']) * 100.0

        avg_pct = average / fee.max_amount * 100.0

        avg_category_pct[fee.population] += pct
        category_count[fee.population] += 1

        fee_info.append({'fee': fee,
                         'total': total,
                         'average': average,
                         'count': count,
                         'pct': pct,
                         'avg_pct': avg_pct
        })

    stats['num_waivers_ug'] = FeeWaiver.objects.filter(fee__term=term, fee__population=0).values('student__pk',
                                                                                        'student__sunetid',
                                                                                        'student__name').distinct().count()
    stats['num_waivers_grad'] = FeeWaiver.objects.filter(fee__term=term, fee__population=1).values('student__pk',
                                                                                        'student__sunetid',
                                                                                        'student__name').distinct().count()
    stats['pct_waivers_ug'] = float(stats['num_waivers_ug']) / float(stats['enrollment_ug']) * 100.0
    stats['pct_waivers_grad'] = float(stats['num_waivers_grad']) / float(stats['enrollment_grad']) * 100.0

    stats['avg_pct_ug'] = avg_category_pct[0] / float(category_count[0])
    stats['avg_pct_grad'] = avg_category_pct[1] / float(category_count[1])

    stats['total_ug'] = total_waiver[0]
    stats['total_grad'] = total_waiver[1]

    stats['fee_ug'] = total_fee[0]
    stats['fee_grad'] = total_fee[1]

    stats['fees'] = fee_info

    return stats
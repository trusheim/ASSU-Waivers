from assu_waivers.models import Term, Student, Enrollment, FeeWaiver

def GetTermForDate(datetime):
    try:
        term = Term.objects.filter(refund_opens__lte=datetime,refund_closes__gte=datetime).get()
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

def PrnText(text,length):
    if len(text) > length:
        return text[:length]
    return text.ljust(length,' ')

def SunetPaidFee(sunetid,fee):
    try:
        student = Student.objects.get(sunetid=sunetid)
    except Student.DoesNotExist:
        return False,'not_found',"SUID not found in database"

    return StudentPaidFee(student,fee)

def StudentPaidFee(student,fee):
    try:
        enrollment = Enrollment.objects.get(term=fee.term,student=student)
    except Enrollment.DoesNotExist:
        return False, 'not_enrolled', "Student was not listed as enrolled during the fee's term"

    try:
        waiver = FeeWaiver.objects.get(fee=fee,student=student)
    except FeeWaiver.DoesNotExist:
        return True, 'paid', "Student paid the fee and did not waive it."

    return False, 'waived', "Student waived fee with reason: '%s'" % waiver.reason
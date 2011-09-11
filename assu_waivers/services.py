from assu_waivers.models import Term, Student

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

def prnText(text,length):
    if len(text) > length:
        return text[:length]
    return text.ljust(length,' ')
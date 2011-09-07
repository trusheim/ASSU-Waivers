from assu_waivers.models import Term

def GetTermForDate(datetime):
    try:
        term = Term.objects.filter(refund_opens__lte=datetime,refund_closes__gte=datetime).get()
        return term
    except Term.DoesNotExist:
        return None
    except Term.MultipleObjectsReturned:
        return Exception("Multiple terms overlap on " + str(datetime) + ". Failure.")
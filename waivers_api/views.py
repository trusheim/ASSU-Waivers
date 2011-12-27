from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from assu_waivers.models import Term, Student, Fee, Enrollment
from assu_waivers.services import SunetPaidFee
from waivers_api.api import JsonResponse, ERRORS, api
from waivers_api.privileges import requirePrivilege

def not_found(request):
    return JsonResponse.BadRequestError()

@requirePrivilege('__ACTIVE__')
@api
def test(request,api_key):
    return JsonResponse("API key accepted! This is a test page.").toHttpResponse()

@requirePrivilege('basicData')
@api
def getFees(request,api_key):
    termName = request.GET.get('term')
    term = get_object_or_404(Term,short_name=termName)

    fees = term.fee_set.all()
    feesShort= [{'id': fee.pk,
                 'name': fee.name,
                 'amount': fee.max_amount,
                 'population': fee.get_population_display()
    } for fee in fees]

    return JsonResponse({'fees': feesShort}).toHttpResponse()

@requirePrivilege('basicData')
@api
def getTerms(request,api_key):
    terms = Term.objects.all()
    termsShort = [{'id': term.short_name,'name': term.long_name} for term in terms]

    return JsonResponse({'terms': termsShort}).toHttpResponse()


@requirePrivilege('__ACTIVE__')
@api
def checkFeeStatus(request,api_key):
    feeId = request.GET.get('fee')
    sunetId = request.GET.get('sunetid')

    status = "UNKNOWN"
    description = ""

    fee = get_object_or_404(Fee,pk=feeId)

    paid, status, description = SunetPaidFee(sunetId,fee)

    response = {
        'paid': paid,
        'code': status,
        'description': description
    }

    return JsonResponse(response).toHttpResponse()
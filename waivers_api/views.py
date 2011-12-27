from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from assu_waivers.models import Term, Student, Fee, Enrollment
from assu_waivers.services import SunetPaidFee
from waivers_api.api import JsonResponse, ERRORS, api
from waivers_api.privileges import requirePrivilege, nameHasPrivilege

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

# viewStudent is like master power.
# add viewFee-SPECIFIC, then viewFee-(fee ID) for individual access
@requirePrivilege(('viewStudent','viewFee-SPECIFIC'))
@api
def checkFeeStatus(request,api_key):
    feeId = request.GET.get('fee')
    sunetId = request.GET.get('sunetid')
    fee = get_object_or_404(Fee,pk=feeId)

    # permissions checking (more fine-grained)
    if not nameHasPrivilege(api_key,'viewStudent'):
        if not nameHasPrivilege(api_key,'viewFee-%d' % fee.pk):
            return JsonResponse.BadApiKeyError()

    paid, status, description = SunetPaidFee(sunetId,fee)

    response = {
        'paid': paid,
        'code': status,
        'description': description
    }

    return JsonResponse(response).toHttpResponse()

@requirePrivilege('viewStudent')
@api
def viewStudent(request,api_key):
    sunetid = request.GET.get('sunetid')
    student = get_object_or_404(Student,sunetid=sunetid)

    waivers = student.feewaiver_set.all()
    waiversShort = [{
        'id': waiver.fee.pk,
        'term': waiver.fee.term.short_name,
        'percent': float(waiver.amount) / waiver.fee.max_amount,
        'reason': waiver.reason
    } for waiver in waivers]

    print waiversShort
    return JsonResponse({'waivers': waiversShort}).toHttpResponse()
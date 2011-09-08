from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import BaseModelFormSet
from assu_waivers.models import FeeWaiver, Fee

__author__ = 'trusheim'

class WaiverForm(forms.Form):
    fee = None
    student = None
    waiver_amount = forms.FloatField()

    def __init__(self,fee, student,*args,**kwargs):
        super(WaiverForm,self).__init__(*args,**kwargs)
        self.fee = fee
        self.student = student
        self.waiver_amount = forms.FloatField(self.fee.max_amount,0)
        self.initial['waiver_amount'] = 0

    def set_current(self,amount):
        self.initial['waiver_amount'] = amount

    def clean(self):
        if self.cleaned_data.get('waiver_amount') > self.fee.max_amount:
            raise forms.ValidationError("You may not request a waiver greater than this fee amount.")
        return self.cleaned_data

    def save(self):
        new_amount = self.cleaned_data.get('waiver_amount')

        # save new fee waiver if required
        if self.cleaned_data.get('waiver_amount') > 0:
            waiver = FeeWaiver.objects.get_or_create(student=self.student,fee=self.fee, defaults={'amount': new_amount})[0]
            waiver.amount = new_amount
            waiver.save()

        # delete fee waiver if we newly set a 0
        if self.cleaned_data.get('waiver_amount') <= 0 and self.initial.get('waiver_amount') > 0:
            try:
                waiver = FeeWaiver.objects.get(student=self.student, fee=self.fee)
                waiver.delete()
            except FeeWaiver.DoesNotExist:
                pass

        # if they set 0 and had 0 before, don't make a new waiver.

    @staticmethod
    def get_list(term,student,*args,**kwargs):

        # load up some datums
        fees = Fee.objects.filter(term=term,population=student.population)

        # setup fee forms
        forms = []
        for fee in fees:
            form = WaiverForm(fee,student,prefix=str(fee.pk),*args,**kwargs)
            waiver = fee.feewaiver_set.filter(student=student)
            if waiver.count():
                form.set_current(waiver.get().amount)
            forms.append(form)

        forms.sort(cmp=lambda x,y: x.fee.pk < y.fee.pk)

        return forms

    @staticmethod
    def verify_list(list):
        for form in list:
            if not form.is_valid():
                return False
        return True

    @staticmethod
    def save_list(list):
        for form in list:
            form.save()
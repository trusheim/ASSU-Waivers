from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import BaseModelFormSet
from assu_waivers.models import FeeWaiver, Fee, Student, Enrollment

__author__ = 'trusheim'


class WaiverForm(forms.Form):
    fee = None
    student = None
    waiver_amount = forms.FloatField()
    reason_burden = forms.BooleanField(required=False)
    reason_morally = forms.BooleanField(required=False)
    reason_value = forms.BooleanField(required=False)
    reason_other = forms.BooleanField(required=False)
    reason_other_expository = forms.CharField(required=False, initial="")

    def __init__(self, fee, student, *args, **kwargs):
        super(WaiverForm, self).__init__(*args, **kwargs)
        self.fee = fee
        self.student = student
        self.waiver_amount = forms.FloatField(self.fee.max_amount, 0)
        self.initial['waiver_amount'] = 0

    def set_current(self, waiver):
        self.initial['waiver_amount'] = waiver.amount
        self.initial['reason_other'] = True
        self.initial['reason_other_expository'] = waiver.reason

    def clean(self):
        if self.cleaned_data.get('waiver_amount') > self.fee.max_amount:
            raise forms.ValidationError("You may not request a waiver greater than this fee amount.")

        if self.cleaned_data.get('waiver_amount') == 0:
            return self.cleaned_data # no more validation needed if no waiver

        if not (self.cleaned_data.get('reason_burden') or self.cleaned_data.get('reason_morally') or \
                    self.cleaned_data.get('reason_value') or self.cleaned_data.get('reason_other')):
            raise forms.ValidationError("You must select a reason to request a waiver from this fee.")

        if self.cleaned_data.get('reason_other') \
            and (not self.cleaned_data.get('reason_other_expository')
                 or self.cleaned_data.get("reason_other_expository") is None
                 or self.cleaned_data.get("reason_other_expository") == ""):
            raise forms.ValidationError("Please provide an 'other' reason.")

        return self.cleaned_data

    def save(self):
        new_amount = self.cleaned_data.get('waiver_amount')

        # build the reasons field by concat'ing the reasons.
        reasons = ""
        if self.cleaned_data.get('reason_burden'):
            reasons += "I cannot afford this amount because this student fee will be a significant financial burden. "
        if self.cleaned_data.get('reason_morally'):
            reasons += "I am morally and ethically opposed to this group's mission. "
        if self.cleaned_data.get('reason_value'):
            reasons += "I do not find value from this group. "
        if self.cleaned_data.get('reason_other'):
            reasons += self.cleaned_data.get('reason_other_expository')

        # save new fee waiver if required
        if self.cleaned_data.get('waiver_amount') > 0:
            waiver = FeeWaiver.objects.get_or_create(student=self.student, fee=self.fee, defaults={'amount': new_amount})[0]
            waiver.amount = new_amount
            waiver.reason = reasons
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
    def get_list(enrollment, *args, **kwargs):

        # load up some datums
        fees = Fee.objects.filter(term=enrollment.term, population=enrollment.population)

        # setup fee forms
        forms = []
        for fee in fees:
            form = WaiverForm(fee, enrollment.student, prefix=str(fee.pk), *args, **kwargs)
            waiver = fee.feewaiver_set.filter(student=enrollment.student)
            if waiver.count():
                form.set_current(waiver.get())
            forms.append(form)

        forms.sort(cmp=lambda x, y: x.fee.pk < y.fee.pk)

        return forms

    @staticmethod
    def verify_list(newlist):
        for form in newlist:
            if not form.is_valid():
                return False
        return True

    @staticmethod
    def save_list(newlist):
        for form in newlist:
            form.save()


class StudentUploadForm(forms.Form):
    csv = forms.FileField(label="Student data CSV")
    athletes = forms.FileField(label="Athlete Exception CSV")

class AdminWaiverForm(forms.Form):
    sunets = forms.CharField(required=True, widget=forms.Textarea)

    def clean_sunets(self):
        sunetBlock = str(self.cleaned_data.get('sunets'))

        errors = []
        sunets = []

        lines = sunetBlock.splitlines()
        for line in lines:
            individuals = line.split(',')

            for individual in individuals:
                individual = individual.lower().strip()
                individual = individual.replace("@stanford.edu","")
                if not self.sunet_is_valid_form(individual):
                    errors.append('%s is not proper form for a SUNetID' % individual)
                    continue

                try:
                    record = Student.objects.get(sunetid=individual)
                except Exception:
                    errors.append("%s is not recognized as a student in the waivers system for this term" % individual)
                    continue

                sunets.append(individual)
            if len(errors) > 0:
                raise forms.ValidationError(errors)
        return sunets

    def sunet_is_valid_form(self,sunet):
        individual = sunet.lower().strip()
        individual = individual.replace("@stanford.edu","")
        if not individual.isalnum() or len(individual) > 8:
            return False
        return True

    def save(self, term):
        sunets = self.cleaned_data.get('sunets')
        print "SAVING %d SUNETS" % len(sunets)

        for sunet in sunets:
            try:
                print sunet
                student = Student.objects.get(sunetid=sunet)
                print student
                enrollment = Enrollment.objects.get(term=term, student=student)
                print enrollment
                waiveable = Fee.objects.filter(term=term,population=enrollment.population)
                print "Found %d waivers" % len(waiveable)
                for fee in waiveable:
                    waiver = FeeWaiver.objects.get_or_create(student=student, fee=fee, defaults={'amount': 0})[0]
                    waiver.amount = fee.max_amount
                    waiver.reason = "Administrative fee waiver"
                    waiver.save()
            except Exception:
                pass
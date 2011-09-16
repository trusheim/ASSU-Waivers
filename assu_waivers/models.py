from django.db import models

POPULATIONS = ((0, "Undergraduate"), (1, "Graduate"), (2, "Law"), )

class Term(models.Model):
    short_name = models.SlugField(max_length=5,blank=False, verbose_name="Term", help_text="e.g. A1011, W1011, S1011 (max 5 letters & numbers, no spaces)")
    long_name = models.CharField(max_length=128, blank=False, verbose_name="Term name", help_text="e.g. Winter 2010-2011")
    refund_opens = models.DateTimeField(blank=False, verbose_name="Date/time this waiver period opens", help_text="8:00 AM on the first day of the quarter")
    refund_closes = models.DateTimeField(blank=False, verbose_name="Date/time this waiver period closes", help_text="5:00 PM on the second Friday of the quarter")

    def __unicode__(self):
        return self.long_name

class Student(models.Model):
    suid = models.CharField(max_length=8, primary_key=True, verbose_name="SUID #", help_text="e.g. 05555555")
    sunetid = models.CharField(max_length=8, verbose_name='SUNetID',help_text="e.g. joeblow")
    name = models.CharField(max_length=128, verbose_name='Full Name',help_text="e.g. Joe Q Blow")
    no_waiver = models.BooleanField(default=False, verbose_name="No Waivers Allowed", help_text="This student may not receive any waivers (e.g., because he/she is an NCAA athlete)")
    terms = models.ManyToManyField(Term,through="Enrollment")

    def __unicode__(self):
        return self.sunetid

    @staticmethod
    def popFromRegistrarStatus(registrar_status):
        if registrar_status == "UG":
            return 0
        elif registrar_status == "G":
            return 1
        else:
            raise Exception("Unexpected registration status provided")

class Enrollment(models.Model):
    student = models.ForeignKey(Student)
    term = models.ForeignKey(Term)
    population = models.IntegerField(choices=POPULATIONS)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'term')

    def __unicode__(self):
        return "%s (%s)" % (self.student.sunetid, self.term.short_name)


class Fee(models.Model):
    name = models.CharField(max_length=128, verbose_name="Fee name",help_text="Group name or general fee name")
    population = models.IntegerField(choices=POPULATIONS, help_text="May only be applied to one population. Create multiple identically named fees if necessary.")
    term = models.ForeignKey(Term)
    max_amount = models.FloatField(blank=False)

    def __unicode__(self):
        return "%s (%s)" % (self.name,self.term)

class FeeWaiver(models.Model):
    student = models.ForeignKey(Student)
    fee = models.ForeignKey(Fee)
    amount = models.FloatField()
    reason = models.TextField()
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student','fee')
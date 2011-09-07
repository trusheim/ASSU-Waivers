from django.db import models

POPULATIONS = ((0, "Undergraduate"), (1, "Graduate"), (2, "Law"), )

class Student(models.Model):
    sunetid = models.CharField(max_length=8, verbose_name='SUNetID',help_text="e.g. joeblow")
    suid = models.CharField(max_length=8, primary_key=True, verbose_name="SUID #", help_text="e.g. 05555555")
    no_waiver = models.BooleanField(default=False, verbose_name="No Waivers Possible", help_text="This student may not receive any waivers (e.g., because he/she is an NCAA athlete)")
    population = models.IntegerField(choices=POPULATIONS)

    def __unicode__(self):
        return self.sunetid

class Term(models.Model):
    short_name = models.SlugField(max_length=6,blank=False, verbose_name="Short name", help_text="e.g. A10-11, W10-11, S10-11 (max 6 letters & numbers, no spaces)")
    long_name = models.CharField(max_length=128, blank=False, verbose_name="Long name", help_text="e.g. Winter 2010-2011")
    refund_opens = models.DateTimeField(blank=False, verbose_name="Date/time this waiver period opens", help_text="8:00 AM on the first day of the quarter")
    refund_closes = models.DateTimeField(blank=False, verbose_name="Date/time this waiver period closes", help_text="5:00 PM on the third Friday of the quarter")

    def __unicode__(self):
        return self.long_name

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

    class Meta:
        unique_together = ('student','fee')
from django.db import models

POPULATIONS = ((0, "Undergraduate"), (1, "Graduate"), )


class Term(models.Model):
    short_name = models.SlugField(max_length=5,blank=False, verbose_name="Term", help_text="SSC short code for the quarter - see <a href ='/reports/term_info'>this document</a>")
    long_name = models.CharField(max_length=128, blank=False, verbose_name="Term name", help_text="e.g. Winter 2010-2011")
    refund_opens = models.DateTimeField(blank=False, verbose_name="Date/time this waiver period opens", help_text="8:00 AM on the first day of the quarter. The system will automatically open at this date/time.")
    refund_closes = models.DateTimeField(blank=False, verbose_name="Date/time this waiver period closes", help_text="5:00 PM on the second Friday of the quarter. The system will automatically close at this date/time.")

    def __unicode__(self):
        return self.long_name


class Student(models.Model):
    suid = models.CharField(max_length=8, primary_key=True, verbose_name="SUID #", help_text="e.g. 05555555")
    sunetid = models.CharField(max_length=8, verbose_name='SUNetID',help_text="e.g. joeblow")
    name = models.CharField(max_length=128, verbose_name='Full Name',help_text="e.g. Blow,Joe Q")
    no_waiver = models.BooleanField(default=False, verbose_name="No Waivers Allowed", help_text="This student may not receive any waivers (e.g., because he/she is an NCAA athlete)")
    terms = models.ManyToManyField(Term,through="Enrollment")

    def __unicode__(self):
        return self.sunetid

    @staticmethod
    def popFromRegistrarStatus(status):
        if status == "UG":
            return 0
        elif status == "GR" or status == "LAW" or status == "GSB" or status == "MED":
            return 1
        else:
            raise Exception("Unexpected registration status provided: %s" % status)


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
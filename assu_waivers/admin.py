from django.contrib import admin
from assu_waivers.models import Student, Fee, Term, FeeWaiver, Enrollment

__author__ = 'trusheim'

class StudentAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('suid','sunetid','no_waiver')
    list_editable = ('no_waiver',)
    search_fields = ('suid','sunetid')
    ordering = ('suid',)
    list_per_page=200

admin.site.register(Student, StudentAdmin)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display=('student','term','population')
    search_fields = ('student__suid','student__sunetid')
    list_filter = ('term__short_name',)
    ordering=('term','student')
    list_per_page=200

admin.site.register(Enrollment,EnrollmentAdmin)

admin.site.register(Term)

class FeeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name','term','population','max_amount',)
    list_filter=('term',)
    search_fields = ('name',)
    ordering = ('term','name')
    list_per_page=100

admin.site.register(Fee,FeeAdmin)

class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ('fee','student','amount',)
    list_filter=('fee','fee__term__short_name','student__suid')
    search_fields=('student__suid','student__sunetid','fee__term__short_name')
    ordering = ('fee','student')
    list_per_page=100

admin.site.register(FeeWaiver,FeeWaiverAdmin)

from django.contrib import admin
from assu_waivers.models import Student, Fee, Term, FeeWaiver

__author__ = 'trusheim'

class StudentAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('suid','sunetid','no_waiver','population')
    list_editable = ('no_waiver',)
    ordering = ('suid',)
    list_per_page=200

admin.site.register(Student, StudentAdmin)

admin.site.register(Term)

class FeeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name','term','population','max_amount',)
    list_filter=('term',)
    ordering = ('term','name')
    list_per_page=100

admin.site.register(Fee,FeeAdmin)

class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ('fee','student','amount',)
    list_filter=('student','fee')
    ordering = ('fee','student')
    list_per_page=100

admin.site.register(FeeWaiver,FeeWaiverAdmin)

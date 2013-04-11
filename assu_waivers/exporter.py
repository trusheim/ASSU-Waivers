import StringIO
import codecs
import csv
from datetime import datetime
from django.db.models.aggregates import Sum
from assu_waivers.models import FeeWaiver, Student
from xlwt import *

__author__ = 'trusheim'


def exportTermToCSV(term):
    datetime_text = datetime.now().strftime("%y-%m-%d-%H-%M")

    output = StringIO.StringIO()
    output.truncate(0)  # sometimes stringIO is left over from a previous function call, idk why
    obuffer = codecs.getwriter("utf-8")(output)
    output_csv = csv.writer(obuffer)

    total_waiver = 0
    num_reqs = 0
    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk', ).annotate(total_amount=Sum('amount'))

    output_csv.writerow([u'SUID', u'Name', u'Type', u'Total Waiver', u'Term', u'Reference Date'])

    for waiver in waivers:
        num_reqs += 1
        student_info = Student.objects.get(pk=waiver['student__pk'])
        amount_text = "%.2f" % waiver['total_amount']
        total_waiver += waiver['total_amount']

        output_csv.writerow([
            str(waiver['student__pk']),
            student_info.name.encode('ascii', 'replace'),
            '700000000001',
            amount_text,
            term.short_name,
            datetime_text
        ])

    final = output.getvalue()
    output.close()
    return final

def exportTermWaiversToExcel(term):
    wb = Workbook()
    ms = wb.add_sheet('Waivers for %s' % term.long_name)

    datetime_text = datetime.now().strftime("%y-%m-%d-%H-%M")

    # header rows
    bold_style = XFStyle()
    bold_font = Font()
    bold_font.bold = True
    bold_style.font = bold_font

    ms.write(0, 0, "ASSU quarter fee waiver report", bold_style)
    ms.write(0, 2, "%s (%s)" % (term.long_name, term.short_name), bold_style)
    ms.write(0, 5, "Exported %s" % datetime.now().strftime("%m/%d/%Y %H:%M"), bold_style)
    ms.write(1, 0, "This data is confidential. Disclosure is prohibited without the express consent of the ASSU Financial Manager, or his/her designee.")
    ms.write(3, 0, "Student ID", bold_style)
    ms.write(3, 1, "Name", bold_style)
    ms.write(3, 2, "SSC Code", bold_style)
    ms.write(3, 3, "Total waiver", bold_style)
    ms.write(3, 4, "Term", bold_style)
    ms.write(3, 5, "Reference date", bold_style)
    start_row = 4

    # styling
    ms.col(1).width = 8000
    ms.col(2).width = 3800
    ms.col(4).width = 2000
    ms.col(5).width = 4000

    currency_format = XFStyle()
    currency_format.num_format_str = '"$"#,##0.00_);("$"#,##'


    waivers = FeeWaiver.objects.filter(fee__term=term).values('student__pk', ).annotate(total_amount=Sum('amount'))
    num_reqs = 0

    for waiver in waivers:
        row = start_row + num_reqs
        student_info = Student.objects.get(pk=waiver['student__pk'])

        ms.write(row, 0, str(waiver['student__pk']))
        ms.write(row, 1, student_info.name.encode('ascii', 'replace'))
        ms.write(row, 2, '700000000001')
        ms.write(row, 3, waiver['total_amount'], currency_format)
        ms.write(row, 4, term.short_name)
        ms.write(row, 5, datetime_text)

        num_reqs += 1

    ms.write(start_row + num_reqs, 3, Formula("SUM(D%d:D%d)" % (start_row + 1, start_row + num_reqs)), currency_format)

    # export to string
    output = StringIO.StringIO()
    output.truncate(0)  # sometimes stringIO is left over from a previous function call, idk why
    wb.save(output)
    final = output.getvalue()
    output.close()
    return final
import StringIO
import codecs
import csv
from datetime import datetime
from django.db.models.aggregates import Sum
from assu_waivers.models import FeeWaiver, Student, Enrollment
from xlwt import *

__author__ = 'trusheim'


def exportTermWaiversToCSV(term):
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

    return excelToString(wb)


def exportFeeJBLSummaryToExcel(fee):
    waivers = fee.feewaiver_set.select_related().order_by('student__suid').all()

    total_waiver = fee.feewaiver_set.aggregate(Sum('amount'))['amount__sum']
    if total_waiver is None:
        total_waiver = 0

    total_enrollment = Enrollment.objects.filter(term=fee.term, population=fee.population).count()
    if total_enrollment == 0:
        total_enrollment = 1  # div by 0 fix

    pct_waived = float(waivers.count()) / float(total_enrollment) * 100.0

    wb = Workbook()
    ms = wb.add_sheet('%s (%s)' % (fee.name, fee.term.long_name))

    # header rows
    bold_style = XFStyle()
    bold_font = Font()
    bold_font.bold = True
    bold_style.font = bold_font

    header_style = easyxf('font: height 300, bold 1;')

    warning_style = easyxf('align: wrap 1, vert center; border: top thick, right thick, bottom thick, left thick;')

    ms.write_merge(0, 0, 0, 2, "JBL Fee Waiver Report", header_style)
    ms.write(0, 3, "%s (%s)" % (fee.name, fee.term.long_name), header_style)
    ms.write(1, 3, "Reported: %s" % datetime.now().strftime("%m/%d/%Y %H:%M"))
    ms.write_merge(r1=2, c1=0, r2=8, c2=3, label=getJBLText(), style=warning_style)
    ms.write_merge(r1=9, c1=0, r2=9, c2=3, label="")
    ms.write(10, 0, "Total waived: $%.02f by %d students (%.01f%%)" % (total_waiver, waivers.count(), pct_waived), bold_style)
    ms.write(11, 0, "Name", bold_style)
    ms.write(11, 1, "SUNetID", bold_style)
    ms.write(11, 2, "SUID #", bold_style)
    ms.write(11, 3, "Reason(s)", bold_style)
    start_row = 12

    # styling
    ms.col(0).width = 6000
    ms.col(1).width = 2500
    ms.col(2).width = 2500
    ms.col(3).width = 30000

    ms.set_panes_frozen(True)
    ms.set_horz_split_pos(12)
    ms.set_remove_splits(True)

    num_reqs = 0

    for waiver in waivers:
        row = start_row + num_reqs
        student_info = waiver.student

        ms.write(row, 0, student_info.name.encode('ascii', 'replace'))
        ms.write(row, 1, student_info.sunetid)
        ms.write(row, 2, student_info.suid)
        ms.write(row, 3, waiver.reason)

        num_reqs += 1

    return excelToString(wb)


def excelToString(workbook):
    output = StringIO.StringIO()
    output.truncate(0)  # sometimes stringIO is left over from a previous function call, idk why
    workbook.save(output)
    final = output.getvalue()
    output.close()
    return final

def getJBLText():
    return "To the group President, Financial Officer, and other key officers: " \
    "This document is prepared, pursuant to the ASSU Joint Bylaws, to inform you of the students who have received a " \
    "fee waiver from your group. You are to use this document ONLY to ensure that students who have received a waiver " \
    "do not participate in your group's services. \n\n" \
    "This document is private, and you may not share it outside the officers listed on your application in OrgSync. " \
    "Spreading this document beyond these authorized users may be considered a violation of the Fundamental Standard " \
    "or Governing Documents of the ASSU, and the student(s) whose privacy rights are infringed may have standing to file " \
    "a case against you and/or your group in the Organizational Conduct Board, Office of Community Standards, " \
    "and/or ASSU Constitutional Council."
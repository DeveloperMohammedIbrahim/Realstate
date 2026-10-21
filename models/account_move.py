from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    property_id = fields.Many2one('property')


    def action_do_something(self):
        print("inside action_do_something " * 10, self)

    price_total_words = fields.Char(string="Price Total in Words", compute='_compute_price_total_words')

    def _number_to_words(self, number):
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        thousands = ["", "Thousand", "Million", "Billion"]

        if number == 0:
            return "Zero"

        words = ""
        if number < 0:
            words = "Minus "
            number = -number

        def _convert_chunk(num):
            chunk_words = ""
            if num >= 100:
                chunk_words += units[num // 100] + " Hundred "
                num %= 100
            if num >= 20:
                chunk_words += tens[num // 10] + " "
                num %= 10
            if num >= 10:
                chunk_words += teens[num - 10] + " "
                num = 0
            if num > 0:
                chunk_words += units[num] + " "
            return chunk_words

        chunk_count = 0
        while number > 0:
            chunk = number % 1000
            if chunk > 0:
                words = _convert_chunk(chunk) + thousands[chunk_count] + " " + words
            number //= 1000
            chunk_count += 1

        return words.strip()

    @api.depends('amount_total', 'currency_id')
    def _compute_price_total_words(self):
        for line in self:
            amount = line.amount_total
            if amount:
                currency = line.currency_id
                currency_unit_name = currency.currency_unit_label or "Dirhams"
                currency_subunit_name = currency.currency_subunit_label or "Fils"

                integer_part = int(amount)
                decimal_part = int(round((amount - integer_part) * 100))

                integer_words = self._number_to_words(integer_part) + " " + currency_unit_name
                if decimal_part > 0:
                    decimal_words = self._number_to_words(decimal_part) + " " + currency_subunit_name
                else:
                    decimal_words = ""

                line.price_total_words = (integer_words + " & " + decimal_words).strip() + " Only"
            else:
                line.price_total_words = ""
from odoo.tools.misc import xlsxwriter
from io import BytesIO

class AccountMoveXlsx(models.AbstractModel):
    _name = 'report.app_one.report_invoice_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, invoices):
        # إنشاء ورقة العمل
        sheet = workbook.add_worksheet('Invoice Report')

        # تنسيقات

        bold = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        currency_format = workbook.add_format(
            {'num_format': '#,##0.00', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
        source_format = workbook.add_format({'bold': True, 'align': 'left'})
#bold: يستخدم لتنسيق النصوص بخط عريض مع حدود ومحاذاة النص في الوسط.
# border_format: يستخدم لتنسيق الخلايا بإضافة حدود ومحاذاة النص في الوسط.
# currency_format: يستخدم لتنسيق القيم الرقمية كعملة، ويظهر الأرقام بتنسيق "#,##0.00".
# header_format: تنسيق مخصص للعناوين، بخط عريض وحجم خط 14 ومحاذاة النص في الوسط.
# source_format: تنسيق لخلايا الحقل "Source" بحيث تكون بخط عريض ومحاذاة لليسار.

        # إعداد عرض الأعمدة
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 9.5*3.1)
        sheet.set_column('C:C', 9.5*1.02)
        sheet.set_column('D:D', 9.5*2)
        sheet.set_column('E:E', 9.5*2.65)
        sheet.set_column('F:F', 9.5*1.75)
        sheet.set_column('G:G', 9.5*1.8)

        # إضافة عنوان التقرير
        sheet.merge_range('A1:G1', 'Invoice Report', header_format)

        row = 2  # بدء الكتابة من الصف الثالث

        for invoice in invoices:
            # إضافة الحقل 'Source' في جدول منفصل فوق التفاصيل
            sheet.write(row, 0, 'Source:', source_format)
            sheet.write(row, 1, invoice.invoice_origin or 'N/A', border_format)

            # إضافة فراغ تحت الجدول المنفصل
            row += 2

            # إضافة العناوين
            headers = [
                'S/NO',
                'Job Description',
                'Quantity',
                'Rate per Month/Hour',
                'Total Before VAT Amount',
                'VAT Amount 5%',
                'Total Invoice Amount'
            ]
            for col_num, header in enumerate(headers):
                sheet.write(row, col_num, header, bold)

            row += 1
            serial_no = 1

            for line in invoice.invoice_line_ids:
                sheet.write(row, 0, serial_no, border_format)
                sheet.write(row, 1, line.name or '', border_format)
                sheet.write(row, 2, line.quantity or 0, border_format)
                sheet.write(row, 3, line.price_unit or 0.0, currency_format)
                sheet.write(row, 4, line.price_subtotal or 0.0, currency_format)
                vat_amount = line.price_total - line.price_subtotal
                sheet.write(row, 5, vat_amount or 0.0, currency_format)
                sheet.write(row, 6, line.price_total or 0.0, currency_format)

                row += 1
                serial_no += 1

            # إضافة المجاميع
            sheet.write(row, 3, 'Total Before VAT:', bold)
            sheet.write(row, 4, invoice.amount_untaxed or 0.0, currency_format)

            row += 1
            sheet.write(row, 3, 'VAT Amount (5%):', bold)
            sheet.write(row, 4, invoice.amount_tax or 0.0, currency_format)

            row += 1
            sheet.write(row, 3, 'Grand Total:', bold)
            sheet.write(row, 4, invoice.amount_total or 0.0, currency_format)

            # إضافة فراغ بين الفواتير
            row += 3

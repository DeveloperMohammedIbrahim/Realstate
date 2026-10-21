



from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    confirmed_user_id = fields.Many2one('res.users', string='Confirmed User', readonly=True)
    property_id = fields.Many2one('property')
    discount = fields.Float()

    def action_report_sale_order_xlsx(self):
        actions = self.env['ir.actions.actions']._for_xml_id('app_one.action_report_sale_order_xlsx_wizard')
        return actions
    def exchange(self):
        print("inside exchange " * 10, self)

    def action_print_hello(self):
        return self.env.ref('app_one.action_report_hello').report_action(self)

    def _prepare_invoice(self):
        # استدعاء الدالة الأصلية
        invoice_values = super(SaleOrder, self)._prepare_invoice()
        invoice_values['property_id']=self.property_id.id
        print(invoice_values)
        return invoice_values















    def action_confirm(self):
        # استدعاء الدالة الأصلية
        res = super(SaleOrder, self).action_confirm()  # تقوم بتأكيد الطلب (Sale Order) وتغيير حالته إلى sale
        # print(res)  # صح
        # print("SaleOrder " * 10)
        res.confirmed_user_id = self.env.user.id
        context = self._context.copy()
        print("understand" * 10,self)

    # def action_confirm(self):
    #     # استدعاء الدالة الأصلية
    #     res = super(SaleOrder, self).action_confirm()  # تقوم بتأكيد الطلب (Sale Order) وتغيير حالته إلى sale
    #     print(res)  # صح
    #     print("SaleOrder " * 10)
    #     res.confirmed_user_id = self.env.user.id
    #
    #     # استدعاء button_validate بعد تأكيد الطلب
    #     # .filtered(lambda p: p.state not in ['done', 'cancel'])
    #     picking = self.picking_ids
    #     if picking:
    #         picking.action_confirm()
    #         # picking.action_assign()
    #         picking.button_validate()
    #
    #     # استدعاء دالة create_invoices من النموذج SaleAdvancePaymentInv بعد التأكيد
    #     advance_payment_wizard = self.env['sale.advance.payment.inv'].create({
    #         'advance_payment_method': 'delivered',  # تحديد الخيار الافتراضي
    #         'sale_order_ids': [(6, 0, self.ids)],
    #     })
    #     print(self.ids)
    #     print(advance_payment_wizard)
    #     advance_payment_wizard.create_invoices()
    #
    #     return res
    price_total_words = fields.Char(string="Price Total in Words", compute='_compute_price_total_words')

















class SaleOrderXlsx(models.AbstractModel):
    _name = 'report.app_one.report_sale_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, orders):
        # قراءة التواريخ واسم العميل من بيانات المعالج
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        partner_id = data.get('partner_id')

        # تصفية الطلبات بناءً على المعايير المدخلة
        domain = [('date_order', '>=', date_from), ('date_order', '<=', date_to)]
        if partner_id:
            domain.append(('partner_id', '=', partner_id))

        orders = self.env['sale.order'].search(domain)

        # إنشاء ورقة العمل
        sheet = workbook.add_worksheet('Sale Order Report')

        # تنسيقات
        bold = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
        source_format = workbook.add_format({'bold': True, 'align': 'left'})

        # إعداد عرض الأعمدة
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 9.5 * 3.1)
        sheet.set_column('C:C', 9.5 * 1.02)
        sheet.set_column('D:D', 9.5 * 2)
        sheet.set_column('E:E', 9.5 * 2.65)
        sheet.set_column('F:F', 9.5 * 1.75)
        sheet.set_column('G:G', 9.5 * 1.8)

        # إضافة عنوان التقرير
        sheet.merge_range('A1:G1', 'Sale Order Report', header_format)

        row = 2  # بدء الكتابة من الصف الثالث

        for order in orders:
            # إضافة الحقل 'Source' في جدول منفصل فوق التفاصيل
            sheet.write(row, 0, 'Source:', source_format)
            sheet.write(row, 1, order.name or 'N/A', border_format)

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
                'Total Order Amount'
            ]
            for col_num, header in enumerate(headers):
                sheet.write(row, col_num, header, bold)

            row += 1
            serial_no = 1

            for line in order.order_line:
                sheet.write(row, 0, serial_no, border_format)
                sheet.write(row, 1, line.name or '', border_format)
                sheet.write(row, 2, line.product_uom_qty or 0, border_format)
                sheet.write(row, 3, line.price_unit or 0.0, currency_format)
                sheet.write(row, 4, line.price_subtotal or 0.0, currency_format)
                vat_amount = line.price_total - line.price_subtotal
                sheet.write(row, 5, vat_amount or 0.0, currency_format)
                sheet.write(row, 6, line.price_total or 0.0, currency_format)

                row += 1
                serial_no += 1

            # إضافة المجاميع
            sheet.write(row, 3, 'Total Before VAT:', bold)
            sheet.write(row, 4, order.amount_untaxed or 0.0, currency_format)

            row += 1
            sheet.write(row, 3, 'VAT Amount (5%):', bold)
            sheet.write(row, 4, order.amount_tax or 0.0, currency_format)

            row += 1
            sheet.write(row, 3, 'Grand Total:', bold)
            sheet.write(row, 4, order.amount_total or 0.0, currency_format)

            # إضافة فراغ بين الطلبات
            row += 3

class SaleOrderXlsx1(models.AbstractModel):
    _name = 'report.app_one.report_sale_order_xlsx1'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, orders):
        # إنشاء ورقة العمل
        sheet = workbook.add_worksheet('Sale Order Report')

        # تنسيقات
        bold = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
        source_format = workbook.add_format({'bold': True, 'align': 'left'})

        # إعداد عرض الأعمدة
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 20)

        # إضافة عنوان التقرير
        sheet.merge_range('A1:G1', 'Sale Order Report', header_format)

        row = 2  # بدء الكتابة من الصف الثالث

        for order in orders:
            # إضافة الحقل 'Source' في جدول منفصل فوق التفاصيل
            sheet.write(row, 0, 'Source:', source_format)
            sheet.write(row, 1, order.name or 'N/A', border_format)

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
                'Total Order Amount'
            ]
            for col_num, header in enumerate(headers):
                sheet.write(row, col_num, header, bold)

            row += 1
            serial_no = 1

            for line in order.order_line:
                sheet.write(row, 0, serial_no, border_format)
                sheet.write(row, 1, line.name or '', border_format)
                sheet.write(row, 2, line.product_uom_qty or 0, border_format)
                sheet.write(row, 3, line.price_unit or 0.0, currency_format)
                sheet.write(row, 4, line.price_subtotal or 0.0, currency_format)
                vat_amount = line.price_total - line.price_subtotal
                sheet.write(row, 5, vat_amount or 0.0, currency_format)
                sheet.write(row, 6, line.price_total or 0.0, currency_format)

                row += 1
                serial_no += 1

            # إضافة المجاميع
            sheet.write(row, 3, 'Total Before VAT:', bold)
            sheet.write(row, 4, order.amount_untaxed or 0.0, currency_format)

            row += 1
            sheet.write(row, 3, 'VAT Amount (5%):', bold)
            sheet.write(row, 4, order.amount_tax or 0.0, currency_format)

            row += 1
            sheet.write(row, 3, 'Grand Total:', bold)
            sheet.write(row, 4, order.amount_total or 0.0, currency_format)

            # إضافة فراغ بين الفواتير
            row += 3
class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        # استدعاء الدالة الأصلية
        res = super(SaleAdvancePaymentInvInherit, self).create_invoices()

        # سلوك مخصص بعد إنشاء الفواتير
        print("create_invoicescreate_invoicescreate_invoices")

        return res

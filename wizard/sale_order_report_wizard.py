from odoo import fields, models
from datetime import datetime

class SaleOrderReportWizard(models.TransientModel):
    _name = 'sale.order.report.wizard'
    _description = 'Sale Order XLSX Report Wizard'

    date_from = fields.Date(string="Date From", required=True, default=datetime.today())
    date_to = fields.Date(string="Date To", required=True, default=datetime.today())
    partner_id = fields.Many2one('res.partner', string="Customer")

    def print_xlsx_report(self):
        # تنفيذ التقرير بناءً على البيانات المدخلة في الـ Wizard
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_id': self.partner_id.id,
        }
        return self.env.ref('app_one.action_report_sale_order_xlsx').report_action(self, data=data)

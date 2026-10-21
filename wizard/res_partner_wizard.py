from odoo import fields,models
class ChangeState(models.TransientModel):
    _name = "res.partner.wizard"


    def action_confirm(self):
        print("555555555action_confirm"*10)

    def action_generate_xlsx_report(self):
        return self.env.ref('app_one.action_report_person_xlsx').report_action(self)

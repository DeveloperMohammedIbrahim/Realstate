from odoo import models, fields


class RelatedPerson(models.Model):
    _name = 'related.person'
    _description = 'Daddy\'s love'

    name = fields.Many2one('person', string="Guardian", ondelete='set null')
    child_id = fields.Many2one(
        'person.line',
        string="Child",
        domain="[('gender', '=', 'male'), ('parent_id', '=', name)]",
        ondelete='set null'
    )

    def action_open_related_person(self):
        self.ensure_one()  # تأكد من وجود سجل فردي فقط
        action = self.env['ir.actions.actions']._for_xml_id('app_one.action_person')
        view_id = self.env.ref('app_one.view_person_form').id
        action['res_id'] = self.name.id
        action['views'] = [(view_id, 'form')]
        return action
class Gift(models.Model):
    _name = 'gift'
    _description = 'Gift'

    name = fields.Char(string="Gift name", required=True)
    price = fields.Float(string="price", required=True)

class Birthday(models.Model):
    _name = 'birthday'
    _description = 'Birthday'

    son = fields.Char(string="اسم الطفل", required=True)
    father = fields.Char(string="اسم الوالد", required=True)
    birthday = fields.Date(string="تاريخ الميلاد", required=True)
    parent_id = fields.Many2one('person', string="الوالد")

    gift_id = fields.Many2one('gift', string="الهدية")  # Field to select the gift
    gift_price = fields.Float(string="سعر الهدية", related='gift_id.price', store=True)  # Field related to the gift price
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_change_state_wizard(self):
        actions = self.env['ir.actions.actions']._for_xml_id('app_one.res_partner_wizard_action')
        return actions
    @api.model
    def _default_property_id(self):
        property_record = self.env['property'].search([('name', '=', 'property')], limit=1)
        # tag_record = self.env['res.partner.category'].search([('name', '=', 'Vendor')], limit=1)

        return property_record if property_record else False

    def _default_category(self):

        p = self.env.context
        for i in p:

            print(i)
            if i == 'res_partner_search_mode':
                if self.env.context['res_partner_search_mode'] == 'supplier':
                    tag_record = self.env['res.partner.category'].search([('name', '=', 'Vendor')], limit=1)
                    print("Vendor" * 100)

                    return tag_record if tag_record else False
                elif self.env.context['res_partner_search_mode'] == 'customer':

                    tag_record = self.env['res.partner.category'].search([('name', '=', 'customer')], limit=1)

                    return tag_record if tag_record else False
        print("Employees" * 100)
        tag_record = self.env['res.partner.category'].search([('name', '=', 'Employees')], limit=1)
        print("d" * 100, p)

        return tag_record if tag_record else False

    category_id = fields.Many2many('res.partner.category', column1='partner_id',
                                   column2='category_id', string='Tags', default=_default_category)

    property_id = fields.Many2one('property', string='Property')
    price = fields.Float(related='property_id.selling_price')

from odoo import models, fields
class Owner(models.Model):
    _name = 'owner'
    _description = 'A description of my model is owner'
    active = fields.Boolean(default=True)

    name = fields.Char(string='Name', required=True )
    phone = fields.Char()
    address = fields.Char()
    property_ids=fields.One2many('property','owner_id')

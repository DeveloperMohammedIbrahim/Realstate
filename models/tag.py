from odoo import models, fields
class Tag(models.Model):
    _name = 'tag'
    _description = 'A description of my model is tags'
    n=fields.Integer()
    name = fields.Char(string='Name', required=True )

    property_ids=fields.Many2many('property')

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PropertyHistory(models.Model):
    _name = 'property.history'
    _description = 'Property History'
    property_id = fields.Many2one('property')
    user_id = fields.Many2one('res.users')
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()
    line_ids = fields.One2many('property.history.line', 'history_id')


class PropertyLines(models.Model):
    _name = 'property.history.line'

    history_id = fields.Many2one('property.history')
    area = fields.Float()
    description = fields.Char()

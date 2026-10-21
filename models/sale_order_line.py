from odoo import models,  api,fields
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'
    discount=fields.Float()
    undelivered = fields.Integer(compute='_compute_undelivered')

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_undelivered(self):
        for line in self:
            line.undelivered = line.product_uom_qty - line.qty_delivered



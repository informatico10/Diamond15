from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    sale_type = fields.Selection([
        ('export', 'Exportación'),
        ('nacional', 'Venta Nacional')
    ], string='Sale Type')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.country_id:
            if self.partner_id.country_id.name == 'Perú':
                self.sale_type = 'nacional'
            else:
                self.sale_type = 'export'
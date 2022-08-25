from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderType(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    sale_type = fields.Selection([
        ('export', 'Exportación'),
        ('nacional', 'Venta Nacional')
    ], string='Tipo Venta')

    @api.model_create_multi
    def create(self, vals):
        res = super(SaleOrderType, self).create(vals)
        if res.partner_id and res.partner_id.country_id:
            if res.partner_id.country_id.name == 'Perú':
                res.sale_type = 'nacional'
                res._origin.sale_type = 'nacional'
            else:
                res.sale_type = 'export'
                res._origin.sale_type = 'export'
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.country_id:
            if self.partner_id.country_id.name == 'Perú':
                self.sale_type = 'nacional'
                self._origin.sale_type = 'nacional'
            else:
                self.sale_type = 'export'
                self._origin.sale_type = 'export'

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    sale_type = fields.Selection([
        ('export', 'Exportación'),
        ('nacional', 'Venta Nacional')
    ], string='Tipo Venta')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.country_id:
            if self.partner_id.country_id.name == 'Perú':
                self.sale_type = 'nacional'
                self._origin.sale_type = 'nacional'
            else:
                self.sale_type = 'export'
                self._origin.sale_type = 'export'
    check_type = fields.Boolean(compute='_compute_check_type', string='Check Type')

    @api.depends('sale_type')
    def _compute_check_type(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.country_id:
                if rec.partner_id.country_id.name == 'Perú':
                    rec.sale_type = 'nacional'
                else:
                    rec.sale_type = 'export'

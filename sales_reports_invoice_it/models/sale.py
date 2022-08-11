from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError
import datetime


class SaleOrderFieldNew(models.Model):
    _inherit = 'sale.order'

    gr = fields.Char('GR')
    oc_partner = fields.Char('Orden de Compra Cliente', required=True)
    set_new_field = fields.Boolean(compute='_compute_set_new_field', string='Set NEw Field')

    @api.depends('oc_partner')
    def _compute_set_new_field(self):
        for rec in self:
            rec.set_new_field = True
            rec.gr = ''
            for pick in rec.picking_ids:
                if pick.state != 'cancel' and pick.despatch_id:
                    rec.gr += pick.despatch_id.name + ', '
            if len(rec.gr) > 3:
                rec.gr = rec.gr[:-2]

    @api.model_create_multi
    def create(self, vals):
        res = super(SaleOrderFieldNew, self).create(vals)
        if len(res.order_line) == 0:
            raise ValidationError('Error debe crear lineas de venta')
        return res


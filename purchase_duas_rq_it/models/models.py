from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrderDuasRqIt(models.Model):
    _inherit = 'purchase.order'

    dua = fields.Char('Dua')
    agency_aduana_id = fields.Many2one('agency.aduana', string='Agencia Aduana')


class StockPickingDuaRQIt(models.Model):
    _inherit = 'stock.picking'

    dua = fields.Char('Dua')
    agency_aduana_id = fields.Many2one('agency.aduana', string='Agencia Aduana')
    check_duas = fields.Boolean(compute='_compute_check_duas', string='Check Duas')

    @api.depends('dua', 'agency_aduana_id')
    def _compute_check_duas(self):
        for rec in self:
            if rec.origin:
                purchase = self.env['purchase.order'].search( [('name', '=', rec.origin)], limit=1 )
                if purchase:
                    rec.dua = purchase.dua
                    rec.agency_aduana_id = purchase.agency_aduana_id.id
                    rec.check_duas = True
                else:
                    rec.dua = False
                    rec.agency_aduana_id = False
                    rec.check_duas = False
            else:
                rec.check_duas = False


class AgencyAduana(models.Model):
    _name = 'agency.aduana'
    _description = 'Agency Aduana'

    name = fields.Char('Agencia')

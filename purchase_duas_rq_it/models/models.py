from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrderDuasRqIt(models.Model):
    _inherit = 'purchase.order'

    dua = fields.Char('Dua')
    agency_aduana_id = fields.Many2one('agency.aduana', string='Agencia Aduana')

    #to contact
    id_partner_to_create = fields.Integer(string='', related='partner_id.id')
    street_partner = fields.Char(string='', related='partner_id.street')
    street2_partner = fields.Char(string='', related='partner_id.street2')
    city_partner = fields.Char(string='', related='partner_id.city')
    state_partner = fields.Many2one('res.country.state', string='', related='partner_id.state_id')
    zip_partner = fields.Char(string='', related='partner_id.zip')
    country_partner = fields.Many2one('res.country', string='', related='partner_id.country_id')

    first_contacto_partner = fields.Many2one('res.partner', string='Atención')
    ids_first_contact = fields.Many2many('res.partner', string='domain by first contact')

    check_domain = fields.Boolean(compute='_compute_check_domain', string='Check Domain')

    @api.depends('ids_first_contact')
    def _compute_check_domain(self):
        for rec in self:
            # TO DOMAIN FIRST CONTACT
            rec.check_domain = True
            if rec.partner_id:
                ar_child = []
                for child in rec.partner_id.child_ids:
                    if child.type == 'contact':
                        ar_child.append(child.id)
                rec.ids_first_contact = ar_child

    @api.onchange('partner_id')
    def _onchange_partner_id_order_report(self):
        for rec in self:
            if self.partner_id:
                ar_child = []
                for child in self.partner_id.child_ids:
                    if child.type == 'contact':
                        ar_child.append(child.id)
                return {
                    'domain': {
                        'first_contacto_partner': [('id', 'in', ar_child)]
                    }
                }


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

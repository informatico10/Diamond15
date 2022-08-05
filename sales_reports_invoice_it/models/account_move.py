from odoo import models, fields, api,tools
import datetime


class AccountMoveSalesReports(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order', string='sale')
    gr = fields.Char('GR')
    oc_partner = fields.Char('Orden de Compra Cliente')
    iqbf = fields.Boolean('IQBF')
    observacion = fields.Text('Observación')

    fch_entrega = fields.Date('Fecha Entrega')
    fch_vencimiento = fields.Date('Fch Vencimiento')

    set_fch_venci = fields.Boolean(compute='_compute_set_fch_venci', string='Set FCh Venci')

    @api.depends('fch_vencimiento')
    def _compute_set_fch_venci(self):
        for rec in self:
            # fch vencimiento
            rec.set_fch_venci = True
            if rec.fch_entrega and rec.invoice_payment_term_id and rec.invoice_payment_term_id.line_ids:
                days = rec.invoice_payment_term_id.line_ids[0].days
                rec.fch_vencimiento = rec.fch_entrega + datetime.timedelta(days=days)

            # SALE
            if rec.invoice_origin:
                sale = self.env['sale.order'].search([('name', '=', rec.invoice_origin)], limit=1)
                if sale:
                    rec.sale_id = sale.id
                    rec.gr = rec.sale_id.gr
                    rec.oc_partner = rec.sale_id.oc_partner
                else:
                    rec.sale_id = False
                    rec.gr = ''
                    rec.oc_partner = ''
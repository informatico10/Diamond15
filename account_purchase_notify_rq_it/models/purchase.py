from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrderStockNotification(models.Model):
    _inherit = 'purchase.order'

    type_purchase = fields.Selection([
        ('0', 'Compra Nacional'),
        ('1', 'Importación')
    ], string='Tipo Compra')

    @api.onchange('partner_id')
    def _onchange_partner_id_type_purchase(self):
        if self.partner_id and self.partner_id.country_id:
            if self.partner_id.country_id.name == 'Perú':
                self.type_purchase = '0'
            else:
                self.type_purchase = '1'

    check_type_purchase = fields.Boolean(compute='_compute_check_type_purchase', string='Check TYpe Purchase')

    @api.depends('type_purchase')
    def _compute_check_type_purchase(self):
        for rec in self:
            rec.check_type_purchase = True
            if rec.partner_id and rec.partner_id.country_id:
                if rec.partner_id.country_id.name == 'Perú':
                    rec.type_purchase = '0'
                else:
                    rec.type_purchase = '1'
            users = self.env.ref('account.group_account_manager').users
            body = '<Admins Facturacion> Factura Creada '
            model = 'account.move'
            for invoice in rec.invoice_ids:
                if invoice.create_notify_admins == False:
                    invoice.message_channel_account(users, body, model)
                    invoice.create_notify_admins = True

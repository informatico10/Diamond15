from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMoveNotifyRqIt(models.Model):
    _inherit = 'account.move'

    invoice_purchase = fields.Selection([
        ('0', 'Adjunto')
    ], string='Factura Proveedor', track_visibility='always')
    field_pdf = fields.Binary('PDF', track_visibility='always')
    field_xml = fields.Binary('XML', track_visibility='always')
    field_cdr = fields.Binary('CDR', track_visibility='always')
    change_pdf = fields.Boolean('change_pdf', default=False)

    @api.onchange('field_pdf')
    def _onchange_field_pdf(self):
        if self.field_pdf:
            self.change_pdf = True
            self._origin.change_pdf = True

    @api.onchange('field_xml')
    def _onchange_field_xml(self):
        if self.field_xml:
            self.field_xml = True
            self._origin.field_xml = True

    @api.onchange('field_cdr')
    def _onchange_field_cdr(self):
        if self.field_cdr:
            self.field_cdr = True
            self._origin.field_cdr = True

    purchase_order_id = fields.Many2one('purchase.order', string='Compra')
    type_purchase = fields.Selection([
        ('0', 'Compra Nacional'),
        ('1', 'Compra Internacional')
    ], string='Tipo Compra', related='purchase_order_id.type_purchase')
    check_fields = fields.Char(compute='_compute_check_fields', string='check_fields')

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountMoveNotifyRqIt, self).create(vals)
        if res.invoice_origin:
            purchase = self.env['purchase.order'].search([ ('name', '=', res.invoice_origin) ], limit=1)
            if purchase:
                self.purchase_order_id = purchase.id
                res.purchase_order_id = purchase.id
        return res

    @api.depends('purchase_order_id')
    def _compute_check_fields(self):
        for rec in self:
            if rec.change_pdf and rec.invoice_purchase == '0':
                users = self.env['res.groups'].search( [('name', '=', 'Administrador de Facturación')], limit=1 ).users
                body = 'Documentos subidos en la Factura '
                model = 'account.move'
                rec.message_channel_account(users, body, model)
                rec.change_pdf = False
            rec.check_fields = True

import base64
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
    
    field_pdf_name = fields.Char(string='Field Pdf Name', required=False)
    field_xml_name = fields.Char(string='Field Xml Name', required=False)
    field_cdr_name = fields.Char(string='Field Cdr Name', required=False)

    change_pdf = fields.Boolean('change_pdf', default=False)

    @api.onchange('field_pdf')
    def _onchange_field_pdf(self):
        if self.field_pdf:
            self.change_pdf = True
            self._origin.change_pdf = True

            self._origin.attachment_ids += self.env['ir.attachment'].sudo().create({
                'name': self.field_pdf_name,
                'res_model': 'account.move',
                'datas': self.field_pdf,
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })

            if self.field_xml:
                self._origin.field_xml = base64.b64encode(self.field_xml)
            if self.field_cdr:
                self._origin.field_cdr = base64.b64encode(self.field_cdr)

    @api.onchange('field_xml')
    def _onchange_field_xml(self):
        if self.field_xml:
            self.change_pdf = True
            self._origin.change_pdf = True

            self._origin.attachment_ids += self.env['ir.attachment'].sudo().create({
                'name': self.field_xml_name,
                'res_model': 'account.move',
                # 'datas': base64.b64encode(new_record.documento),
                'datas': self.field_xml,
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })

            if self.field_pdf:
                self._origin.field_pdf = base64.b64encode(self.field_pdf)
            if self.field_cdr:
                self._origin.field_cdr = base64.b64encode(self.field_cdr)

    @api.onchange('field_cdr')
    def _onchange_field_cdr(self):
        if self.field_cdr:
            self.change_pdf = True
            self._origin.change_pdf = True

            self._origin.attachment_ids += self.env['ir.attachment'].sudo().create({
                'name': self.field_cdr_name,
                'res_model': 'account.move',
                # 'datas': base64.b64encode(new_record.documento),
                'datas': self.field_cdr,
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })

            if self.field_pdf:
                self._origin.field_pdf = base64.b64encode(self.field_pdf)
            if self.field_xml:
                self._origin.field_xml = base64.b64encode(self.field_xml)

    purchase_order_id = fields.Many2one('purchase.order', string='Compra')
    type_purchase = fields.Selection([
        ('0', 'Compra Nacional'),
        ('1', 'Importación')
    ], string='Tipo Compra', related='purchase_order_id.type_purchase')
    check_fields = fields.Char(compute='_compute_check_fields', string='check_fields')

    @api.model
    def create(self, vals):
        res = super(AccountMoveNotifyRqIt, self).create(vals)
        if res.invoice_origin:
            purchase = self.env['purchase.order'].search([ ('name', '=', res.invoice_origin) ], limit=1)
            if purchase:
                self.purchase_order_id = purchase.id
                res.purchase_order_id = purchase.id
        return res

    create_notify_admins = fields.Boolean('Create Notify', default=False)

    def write(self, values):
        self12 = self
        res = super(AccountMoveNotifyRqIt, self).write(values)

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

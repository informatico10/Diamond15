from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrderGroupRqITInvoice(models.Model):
    _inherit = 'purchase.order'

    solicitar_creacion_factura = fields.Boolean('Solicitar Aprobacion', default=False)
    solicitante_creacion_factura_id = fields.Many2one('res.users', string='Solicitante Aprobacion')

    def button_solicitar_creacion_factura(self):
        users = self.env['res.groups'].search( [('name','=','Notificar Creación Factura en Compras')], limit=1).users
        if users:
            body = 'Solitar Creación de Factura en Compra '
            self.message(users, body)
            self.message_post(body=body)
            self.solicitar_creacion_factura = True
            self.solicitante_creacion_factura_id = self.env.user
        else:
            raise ValidationError('No hay Usuarios en el grupo crear Factura en Compras')

    def action_create_invoice(self):
        res = super(PurchaseOrderGroupRqITInvoice, self).action_create_invoice()

        self.solicitar_creacion_factura = True

        users = []
        users_admin_compra = self.env.ref('purchase_invoice_generate_rq_it.group_notify_purchase_generate_invoice').users.ids
        if self.solicitante_creacion_factura_id:
            if len(users_admin_compra) > 0:
                users_admin_compra.append(self.solicitante_creacion_factura_id.id)
            else:
                users_admin_compra = [self.solicitante_creacion_factura_id.id]
        users = self.env['res.users'].search([('id', 'in', users_admin_compra)])
        if len(users) > 0:
            body = 'Factura de Compra Creada'
            self.message(users, body)
            self.message_post(body=body)
        return res

    def button_cancel(self):
        res = super(PurchaseOrderGroupRqITInvoice, self).button_cancel()
        self.solicitar_creacion_factura = False
        self.solicitante_creacion_factura_id = False
        return res

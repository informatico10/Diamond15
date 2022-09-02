from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderPayment(models.Model):
    _inherit = 'sale.order'

    exceeded_credit = fields.Boolean('Credito Excedido', default=False)
    exceeded_credit_approve = fields.Boolean('Credito Excedido Aprobado', default=False)
    exceeded_credit_user_need = fields.Many2one('res.users', string='')

    message_credit_0 = fields.Char(string=' ', default='Credito Superado SIN APROBAR')

    state_payment_sale = fields.Selection([
        ('0', 'Nada a Aprobar'),
        ('1', 'Sin Aprobar'),
        ('2', 'Notificado'),
        ('3', 'Aprobado'),
    ], string='Estado Extra Credito')
    check_credit = fields.Boolean(compute='_compute_check_credit', string='Check Credit')

    pay_detail = fields.Selection([
        ('0', 'Adjuntar Archivo')
    ], string='Detalle de Pago', default='')
    way_pay = fields.Selection([
        ('0', 'Efectivo'),
        ('1', 'Deposito'),
        ('2', 'Transferencia'),
        ('3', 'Tarjeta de Crédito'),
        ('4', 'Cheque'),
    ], string='Forma de Pago')
    pay_file = fields.Binary('Archivo de Pago')
    field_pay_name = fields.Char(string='Field Pay File', required=False)
    change_pay_file = fields.Boolean('Change PAy File', default=False)
    pays_state = fields.Selection([
        ('0', 'Sin Pago'),
        ('1', 'Notificado'),
        ('2', 'Confirmado'),
    ], string='Estado de Pago')

    @api.onchange('pay_file')
    def _onchange_pay_file(self):
        if self.pay_file:
            self.change_pay_file = True
            self._origin.change_pay_file = True

            self._origin.attachment_ids += self.env['ir.attachment'].sudo().create({
                'name': self.field_pay_name,
                'res_model': 'sale.order',
                'datas': self.pay_file,
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })
        else:
            self._origin.change_pay_file = False
            self.change_pay_file = False

    @api.depends('exceeded_credit', 'state_payment_sale', 'pays_state')
    def _compute_check_credit(self):
        for rec in self:
            rec.check_credit = True
            # rec.exceeded_credit
            if rec.partner_id:
                if rec.partner_id.total_due > rec.partner_id.credit_limit_payment:
                    rec.exceeded_credit = True
                else:
                    rec.exceeded_credit = False
            else:
                rec.exceeded_credit = False

            # rec.state_payment_sale
            if rec.exceeded_credit == False:
                rec.state_payment_sale = '0'
            elif rec.exceeded_credit and rec.state in ['sale', 'done']:
                rec.state_payment_sale = '3'
            elif rec.exceeded_credit and rec.state in ['sent', 'draft']:
                if not rec.exceeded_credit_approve:
                    rec.state_payment_sale = '1'
                elif rec.exceeded_credit_approve:
                    rec.state_payment_sale = '2'
            else:
                rec.state_payment_sale = '0'

            # rec.pays_state
            if rec.pay_detail == '':
                rec.pays_state = '0'
            elif rec.pay_detail == '0' and rec.pay_file:
                rec.pays_state = '1'
            if rec.pay_detail == '0' and rec.pay_file and len(rec.invoice_ids) > 0:
                rec.pays_state = '2'
                for invoice in rec.invoice_ids:
                    if invoice.state != 'cancel' and invoice.payment_state != 'paid':
                        rec.pays_state = '1'

            # send to Tesoreros
            if self.change_pay_file:
                body = 'Pago registrado en la Venta '
                model = 'sale.order'
                users = self.env['res.groups'].search( [('name','=','Notificación en Venta a Tesoreria al Registrar PDF pago')] ).users
                self.message_channel(users, body, model, self.id)
                self.change_pay_file = False

    @api.onchange('partner_id')
    def _onchange_partner_id_payment_check(self):
        if self.partner_id:
            if self.partner_id.total_due > self.partner_id.credit_limit_payment:
                self.exceeded_credit = True
            else:
                self.exceeded_credit = False
        else:
            self.exceeded_credit = False

    def action_confirm(self):
        if self.exceeded_credit and self.exceeded_credit_approve == False:
            if not self.env.user.has_group('sale_payment_rq_it.group_payment_sale_extracredit'):
                if self.partner_id and self.partner_id.extra_credit == 'si':
                    return {
                        'name': 'Notificación',
                        'res_model': 'sale.payment.notification',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': {
                            'default_message': '0',
                            'default_sale_id': self.id,
                        },
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
                elif self.partner_id and self.partner_id.extra_credit == 'no':
                    return {
                        'name': 'Notificación',
                        'res_model': 'sale.payment.notification',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': {
                            'default_message': '1',
                            'default_sale_id': self.id
                        },
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
            else:
                if self.partner_id and self.partner_id.extra_credit == 'si':
                    return {
                        'name': 'Notificación',
                        'res_model': 'sale.payment.notification',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': {
                            'default_message': '2',
                            'default_sale_id': self.id
                        },
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }

                if self.partner_id and self.partner_id.extra_credit == 'no':
                    raise ValidationError('Superó Límite de Crédito, el Contacto no tiene la opción de Extra Crédito')

        self.message_credit_0 = 'Credito Superado APROBADO'
        res = super(SaleOrderPayment, self).action_confirm()
        return res

    def action_cancel(self):
        self.exceeded_credit_approve = False
        self.exceeded_credit_user_need = False
        self.message_credit_0 = 'Credito Superado SIN APROBAR'
        res = super(SaleOrderPayment, self).action_cancel()
        return res

    def message_channel(self, users, body_message, model, id):
        if users:
            ch_obj = self.env['mail.channel']
            config = self.env['ir.config_parameter']
            base_url = config.sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=' % (id)
            base_url += model
            body = body_message + ' '
            body += '<a href="%s" class="o_redirect">#%s</a> '%(base_url, self.name)
            body += self.company_id.name
            self.message_post(body=body)
            for user in users:
                if user != self.env.user:
                    ch = ch_obj.sudo().search([ ('name', '=', user.name + ', ' + self.env.user.name), ('channel_type', '=', 'chat') ])
                    if not ch:
                        ch = ch_obj.sudo().search([ ('name', '=', self.env.user.name + ', ' + user.name), ('channel_type', '=', 'chat') ])
                    if not ch:
                        ch = ch_obj.sudo().create({
                                'name': (user.name + ', ' + self.env.user.name),
                                'channel_last_seen_partner_ids': [(0,0,{'partner_id': self.env.user.partner_id.id}),(0,0,{'partner_id': user.partner_id.id})],
                                'public': 'private',
                                'channel_type': 'chat'
                            })
                    ch.message_post(attachment_ids=[], body=body, content_subtype='html', message_type='comment',partner_ids=[], email_from=self.env.user.partner_id.email, author_id=self.env.user.partner_id.id)



class SalePaymentNotification(models.TransientModel):
    _name = 'sale.payment.notification'
    _description = 'Sale Payment Notification'

    message = fields.Selection([
        ('0', 'Superó Límite de Crédito, debe solicitar Aprobación'),
        ('1', 'Superó Límite de Crédito, el Contacto no tiene la opción de Extra Crédito'),
        ('2', 'Superó Límite de Crédito, Confirme Aprobación')
    ], string='Mensaje', readonly=True)
    sale_id = fields.Many2one('sale.order', string='sale')

    def notify(self):
        if self.message == '0':
            body = 'Se solicita aprobar la Venta '
            model = 'sale.order'
            users = self.env['res.groups'].search( [('name','=','Aprobación de Extra-créditos - Ventas')], limit=1 ).users
            self.sale_id.exceeded_credit_user_need = self.env.user.id
            self.sale_id.message_credit_0 = 'Credito Superado NOTIFICADO'
            self.sale_id.message_channel(users, body, model, self.sale_id.id)
        elif self.message == '1':
            body = 'Se solicita permitir al cliente Extracredito '
            model = 'sale.order'
            users = self.env['res.groups'].search( [('name','=','Aprobación de Extra-créditos - Ventas')], limit=1 ).users
            self.sale_id.message_channel(users, body, model, self.sale_id.id)
        elif self.message == '2':
            if self.sale_id.exceeded_credit_user_need:
                body = 'Venta Aprobada '
                model = 'sale.order'
                self.sale_id.message_channel(self.sale_id.exceeded_credit_user_need, body, model, self.sale_id.id)
            self.sale_id.exceeded_credit_approve = True
            self.sale_id.message_credit_0 = 'Credito Superado APROBADO'

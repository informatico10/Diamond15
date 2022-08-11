from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountPaymentRegisterSalePayment(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        account_id = self._context.get('active_ids', [])
        model = self._context.get('active_model', [])
        account = False
        if len(account_id) == 1 and model and model == 'account.move':
            account = self.env['account.move'].search( [('id', '=', account_id[0])] )
            if account.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                users = account.invoice_user_id
                body = 'Pago registrado en la Factura '
                model = 'account.move'
                account.message_channel_account(users, body, model)

        res = super(AccountPaymentRegisterSalePayment, self).action_create_payments()
        return res


class AccountMoveSalePayment(models.Model):
    _inherit = 'account.move'

    def message_channel_account(self, users, body_message, model):
        if users:
            ch_obj = self.env['mail.channel']
            config = self.env['ir.config_parameter']
            base_url = config.sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=' % (self.id)
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


from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderStockNotification(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrderStockNotification, self).action_confirm()

        users = self.env['res.groups'].search( [('name', '=', 'Notificar Responsable de Almacén')] ).users
        users_notify = []
        for user in users:
            if self.warehouse_id in user.warehouse_responsable_id:
                users_notify.append(user)
        model = 'sale.order'
        body = 'Venta con Almacén <span style="color:blue;">' + self.warehouse_id.name + '</span> ha sido Confirmado'
        self.message_channel(users_notify, body, model, self.id)

        return res

    # def message_channel(self, users, body_message, model, id):
    #     if users:
    #         ch_obj = self.env['mail.channel']
    #         config = self.env['ir.config_parameter']
    #         base_url = config.sudo().get_param('web.base.url')
    #         base_url += '/web#id=%d&view_type=form&model=' % (id)
    #         base_url += model
    #         body = body_message + ' '
    #         body += '<a href="%s" class="o_redirect">#%s</a> '%(base_url, self.name)
    #         body += self.company_id.name
    #         self.message_post(body=body)
    #         for user in users:
    #             if user != self.env.user:
    #                 ch = ch_obj.sudo().search([ ('name', '=', user.name + ', ' + self.env.user.name), ('channel_type', '=', 'chat') ])
    #                 if not ch:
    #                     ch = ch_obj.sudo().search([ ('name', '=', self.env.user.name + ', ' + user.name), ('channel_type', '=', 'chat') ])
    #                 if not ch:
    #                     ch = ch_obj.sudo().create({
    #                             'name': (user.name + ', ' + self.env.user.name),
    #                             'channel_last_seen_partner_ids': [(0,0,{'partner_id': self.env.user.partner_id.id}),(0,0,{'partner_id': user.partner_id.id})],
    #                             'public': 'private',
    #                             'channel_type': 'chat'
    #                         })
    #                 ch.message_post(attachment_ids=[], body=body, content_subtype='html', message_type='comment',partner_ids=[], email_from=self.env.user.partner_id.email, author_id=self.env.user.partner_id.id)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPickingGroupRqIT(models.Model):
    _inherit = 'stock.picking'

    solicitar_aprobacion = fields.Boolean('Solicitar Aprobacion', default=False)
    solicitante_aprobacion_id = fields.Many2one('res.users', string='Solicitante Aprobacion')

    def button_solicitar_publicacion(self):
        users = self.env['res.groups'].search( [('name','=','Validar Stock')], limit=1).users
        if users:
            body = 'Solicitar Validar Transferencia'
            self.message(users, body)
            self.message_post(body=body)
            self.solicitar_aprobacion = True
            self.solicitante_aprobacion_id = self.env.user
        else:
            raise ValidationError('No hay Usuarios en el grupo Validar Stock')

    def message(self, users, body_message):
        if users:
            ch_obj = self.env['mail.channel']
            config = self.env['ir.config_parameter']
            base_url = config.sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=stock.picking' % (self.id)
            body = body_message + ' '
            body += '<a href="%s" class="o_redirect">#%s</a> '%(base_url, self.name)
            body += self.company_id.name

            for user in users:
                if user.id != self.env.user.id:
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

    def button_validate(self):
        res = super(StockPickingGroupRqIT, self).button_confirm()

        self.solicitar_aprobacion = True

        users = []
        users_admin_stock = self.env.ref('stock.group_stock_manager').users.ids
        if self.solicitante_aprobacion_id:
            if len(users_admin_stock) > 0:
                users_admin_stock.append(self.solicitante_aprobacion_id.id)
            else:
                users_admin_stock = [self.solicitante_aprobacion_id.id]
        users = self.env['res.users'].search([('id', 'in', users_admin_stock)])
        if len(users) > 0:
            body = 'Stock Validado'
            self.message(users, body)
            self.message_post(body=body)
        return res

    def action_cancel(self):
        res = super(StockPickingGroupRqIT, self).button_cancel()
        self.solicitar_aprobacion = False
        self.solicitante_aprobacion_id = False
        return res

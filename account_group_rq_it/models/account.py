from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMoveGroupRqIT(models.Model):
    _inherit = 'account.move'

    solicitar_aprobacion = fields.Boolean('Solicitar Aprobacion', default=False)
    solicitante_aprobacion_id = fields.Many2one('res.users', string='Solicitante Aprobacion')
    # ver_solicitar_aprobacion = fields.Boolean('Ver SOlicitar Aprobacion')
    # ver_button = fields.Boolean(compute='_compute_ver_button', string='Ver Button')

    # @api.depends('ver_solicitar_aprobacion')
    # def _compute_ver_button(self):
    #     for rec in self:
    #         rec.ver_button = True

    #         if self.env.user.has_group('account_group_rq_it.group_public_invoice') or self.env.user.has_group('account.group_account_manager') or rec.state != 'draft' or rec.solicitar_aprobacion:
    #             rec.ver_solicitar_aprobacion = False
    #         else:
    #             rec.ver_solicitar_aprobacion = True

    def button_solicitar_publicacion(self):
        self.solicitar_aprobacion = True
        users = self.env['res.groups'].search( [('name','=','Publicar Facturas')], limit=1).users
        if users:
            body = 'Solitar Publicar Factura'
            self.message(users, body)
            self.message_post(body=body)
            self.solicitante_aprobacion_id = self.env.user
        else:
            raise ValidationError('No hay Usuarios con la notificación Publicar Facturas')

    def message(self, users, body_message):
        if users:
            self.solicitar_confirmacion = True
            ch_obj = self.env['mail.channel']
            config = self.env['ir.config_parameter']
            base_url = config.sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=account.move' % (self.id)
            body = body_message + ' '
            body += '<a href="%s" class="o_redirect">#%s</a> '%(base_url, self.name)
            body += self.company_id.name

            for user in users:
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
                ch.message_post(attachment_ids=[], body=body, content_subtype='html', message_type='comment',partner_ids=[], subtype='mail.mt_comment', email_from=self.env.user.partner_id.email, author_id=self.env.user.partner_id.id)

    def action_post(self):
        res = super(AccountMoveGroupRqIT, self).action_post()
        if self.solicitante_aprobacion_id:
            users = self.solicitante_aprobacion_id
            body = 'Factura PUBLICADA'
            self.message(users, body)
            self.message_post(body=body)
        return res

    def button_draft(self):
        res = super(AccountMoveGroupRqIT, self).button_draft()
        self.solicitar_aprobacion = False
        self.solicitante_aprobacion_id = False
        return res

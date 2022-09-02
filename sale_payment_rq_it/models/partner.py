from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartnerPayment(models.Model):
    _inherit = 'res.partner'

    payment_condition = fields.Selection([
        ('contado', 'Al Contado'),
        ('credito', 'Crédito'),
    ], string='Condición de Pago', related='property_payment_term_id.payment_condition')

    credit_limit_payment = fields.Float('Límite de Crédito', track_visibility='always')
    currency_credit_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env['res.currency'].search( [('name', '=', 'USD')], limit=1 ), track_visibility='always' )
    extra_credit = fields.Selection([
        ('si', 'Si'),
        ('no', 'No'),
    ], string='Extra Credito', default='no', track_visibility='always')

    @api.onchange('extra_credit')
    def _onchange_extra_credit(self):
        if self.extra_credit == 'no' and self._origin.extra_credit == False:
            return
        elif not self.env.user.has_group('sale_payment_rq_it.group_payment_sale_extracredit'):
            raise ValidationError('Necesita el permiso <Aprobación de Extra-créditos - Ventas> para cambiar el campo')

    @api.onchange('credit_limit_payment')
    def _onchange_credit_limit_payment(self):
        for rec in self:
            rec.due_current = rec.total_due
            rec._origin.due_current = rec.total_due

            rec.remaining_credit = rec.credit_limit_payment - rec.due_current
            rec._origin.remaining_credit = rec.credit_limit_payment - rec.due_current
            if rec.remaining_credit >= 0:
                rec.state_partner = '1'
                rec._origin.state_partner = '1'
            else:
                rec.state_partner = '0'
                rec._origin.state_partner = '0'

    due_current = fields.Float('Deuda Actual', readonly=True)
    remaining_credit = fields.Float('Crédito Restante', readonly=True)
    state_partner = fields.Selection([
        ('0', 'Cliente Moroso'),
        ('1', 'Cliente Estable'),
    ], string='Estado de Cliente', readonly=True)

    check_data_payment = fields.Boolean(compute='_compute_check_data_payment', string='Check DAta Payment')

    @api.depends('due_current', 'remaining_credit', 'state_partner')
    def _compute_check_data_payment(self):
        for rec in self:
            rec.check_data_payment = True
            rec.due_current = rec.total_due
            rec.remaining_credit = rec.credit_limit_payment - rec.due_current
            if rec.remaining_credit >= 0:
                rec.state_partner = '1'
            else:
                rec.state_partner = '0'

    @api.model
    def create(self, values):
        # Add code here
        res = super(ResPartnerPayment, self).create(values)
        identification = res.l10n_latam_identification_type_id
        if identification and identification.id == 6 and res.is_supplier == True and res.country_id and res.country_id.name != 'Perú':
            id_seq = self.env['ir.sequence'].search([('name', '=', 'Contacto, por Importación')], limit=1)
            if not id_seq:
                id_seq = self.env['ir.sequence'].create({
                    'name': 'Contacto, por Importación',
                    'implementation': 'no_gap',
                    'active': True,
                    'prefix': '',
                    'padding': 8,
                    'number_increment': 1,
                    'number_next_actual': 90000000260
                })
            self.vat = id_seq._next()
            res.vat = id_seq._next()

        return res

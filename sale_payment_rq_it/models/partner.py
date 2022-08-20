from odoo import models, fields, api
from odoo.exceptions import ValidationError

	# res_partner_tarifa_plazo_group.view_partner_plazo_pago_readonly_form
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
        if not self.env.user.has_group('sale_payment_rq_it.group_payment_sale_extracredit'):
            raise ValidationError('Necesita el permiso <Aprobación de Extra-créditos - Ventas> para cambiar el campo')

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

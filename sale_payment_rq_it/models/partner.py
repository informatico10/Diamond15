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
        if not self.env.user.has_group('sale_payment_rq_it.group_payment_sale_extracredit'):
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

    def temp_for_change_data(self):
        tamaño = []

        partners = self.env['res.partner'].search([('is_customer', '=', True)])
        tamaño.append(len(partners))

        for partner in partners:
            partner.property_product_pricelist = 2
            partner.property_payment_term_id = 2
            partner.extra_credit = 'si'

        partners = self.env['res.partner'].search([('is_supplier', '=', True), ('l10n_latam_identification_type_id', '=', 14)])
        tamaño.append(len(partners))
        a = partners[0].l10n_latam_identification_type_id.name
        for partner in partners:
            partner.property_product_pricelist = 2
            partner.l10n_latam_identification_type_id = 6

        partners = self.env['res.partner'].search( [('is_supplier', '=', True)] )
        tamaño.append(len(partners))

        for partner in partners:
            partner.lang = 'en_US'
        i = 2


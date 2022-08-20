from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountPaymentTermRqIt(models.Model):
    _inherit = 'account.payment.term'
    _description = 'Account Payment Term'

    payment_condition = fields.Selection([
        ('contado', 'Al Contado'),
        ('credito', 'Crédito'),
    ], string='Condición de Pago')

    check_payment = fields.Boolean(compute='_compute_check_payment', string='Check Payment')

    @api.depends('payment_condition')
    def _compute_check_payment(self):
        for rec in self:
            rec.check_payment = True
            if rec.line_ids:
                rec.payment_condition = ''
                for line in rec.line_ids:
                    if line.value == 'balance':
                        if line.days == 0:
                            rec.payment_condition = 'contado'
                        else:
                            rec.payment_condition = 'credito'
                        break

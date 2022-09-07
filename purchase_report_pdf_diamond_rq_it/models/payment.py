from odoo import api, fields, models


class AccountPaymentTermReportPdf(models.Model):
    _inherit = 'account.payment.term'

    name_english = fields.Char(string='Nombre Ingles / Español', required=False)

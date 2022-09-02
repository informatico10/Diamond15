from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date


class ResPartnerReportPdf(models.Model):
    _inherit = 'res.partner'

    incoterm_diamond = fields.Selection([
        ('0', 'FOB'),
        ('1', 'FCA'),
        ('2', 'CIF'),
        ('3', 'EXwork'),
    ], string='Incoterm')
    incoterm_country_diamond_id = fields.Many2one('res.country', string='Incoterm País')

    @api.onchange('district_id')
    def _onchange_district_id_zip(self):
        if self.district_id:
            self.zip = self.district_id.code
            self._origin.zip = self.district_id.code

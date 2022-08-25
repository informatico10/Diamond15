from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class ResCompanyReportLogo(models.Model):
    _inherit = 'res.company'

    img_report = fields.Binary('Img Report')

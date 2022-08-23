from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date


class ResUsersFirma(models.Model):
    _inherit = 'res.users'

    firma = fields.Binary('Firma')

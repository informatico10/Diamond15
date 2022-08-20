from odoo import models, fields, api,tools
import datetime


class ProductTemplateSalesReport(models.Model):
    _inherit = 'product.template'

    iqbf = fields.Boolean('IQBF')

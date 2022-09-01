from odoo import models, fields, api,tools
import datetime


class ProductTemplateSalesReport(models.Model):
    _inherit = 'product.template'

    iqbf = fields.Boolean('IQBF')

    @api.model
    def create(self, values):
        # Add code here
        res = super(ProductTemplateSalesReport, self).create(values)

        id_seq = self.env['ir.sequence'].search([('name','=','Producto, Código')], limit=1)

        if not id_seq:
            id_seq = self.env['ir.sequence'].create({
                'name': 'Producto, Código',
                'implementation': 'no_gap',
                'active': True,
                'prefix': '',
                'padding': 6,
                'number_increment': 1,
                'number_next_actual': 1001091
            })
        self.default_code = id_seq._next()
        res.default_code = id_seq._next()

        return res

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class StockPickingReportPdf(models.Model):
    _inherit = 'stock.picking'

    # purchase_order_id = fields.Many2one('purchase.order', string='Compra')
    # type_purchase = fields.Selection([
    #     ('0', 'Compra Nacional'),
    #     ('1', 'Importación')
    # ], default="purchase_order_id.type_purchase")

    # check_fields = fields.Char(compute='_compute_check_fields', string='check_fields')


    # @api.depends('purchase_order_id')
    # def _compute_check_fields(self):
    #     for rec in self:
    #         rec.check_fields = True
    #         if rec.origin:
    #             purchase = self.env['purchase.order'].search([ ('name', '=', res.origin) ], limit=1)
    #             if purchase:
    #                 rec.purchase_order_id = purchase.id
    #             else:
    #                 rec.purchase_order_id = False
    #         else:
    #             rec.purchase_order_id = False

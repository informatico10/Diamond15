from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderStockValidationRqIt(models.Model):
    _inherit = 'sale.order'

    # def action_confirm(self):
    #     mensaje = 'No tiene permisos para confirmar venta sin stock suficiente \n\n Productos sin Stock:\n'
    #     no_stock = False
    #     for line in self.order_line:
    #         if line.product_id and line.quantity_available and line.product_uom_qty and line.quantity_available < line.product_uom_qty:
    #             no_stock = True
    #             mensaje += '<' + line.product_id.name + '>'

    #     if not self.env.user.has_group('sale_stock_validation_rq_it.group_confirm_sale_without_stock') and no_stock:
    #         raise ValidationError(mensaje)
    #     return super(SaleOrderStockValidationRqIt, self).action_confirm()


class SaleOrderLineStockValidation(models.Model):
    _inherit = 'sale.order.line'

    quantity_available = fields.Float('Stock')
    check_cant_disponible = fields.Boolean(compute='_compute_check_cant_disponible', string='Check CAnt Disponible')

    @api.depends('quantity_available')
    def _compute_check_cant_disponible(self):
        for rec in self:
            if rec.product_id:
                quants = self.env['stock.quant'].search( [('company_id', '=', rec.company_id.id), ('product_id', '=', rec.product_id.id), ('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id)] )
                rec.quantity_available = 0
                for quant in quants:
                    rec.quantity_available += quant.available_quantity
            rec.check_cant_disponible = True
    
    @api.onchange('product_id')
    def _onchange_product_id_get_quantity_available(self):
        for rec in self:
            if rec.product_id:
                quants = self.env['stock.quant'].search( [('company_id', '=', rec.company_id.id), ('product_id', '=', rec.product_id.id), ('location_id', '=', rec.order_id.warehouse_id.lot_stock_id.id)] )
                rec.quantity_available = 0
                for quant in quants:
                    rec.quantity_available += quant.available_quantity

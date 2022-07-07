# -*- coding: utf-8 -*-

from ast import Pass
from pickle import PicklingError
from shutil import move
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import tools

class product_template(models.Model):
    _inherit = 'product.template'
    
    def unlink(self):
        if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
            t = super(product_template,self).unlink()
            return t
        else:
            raise UserError("No Tiene Los Permisos de 'Manejo Creacion de Productos'")

    @api.model
    def create(self,vals):
        if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
            t = super(product_template,self).create(vals)
            return t
        else:
            raise UserError("No Tiene Los Permisos de 'Manejo Creacion de Productos'")
           
    def write(self,vals):
        if 'seller_ids' or 'name' or 'route_ids' or 'sale_ok' or 'purchase_ok' or 'detailed_type' or 'invoice_policy' or 'expense_policy' or 'uom_id' or 'uom_po_id' or 'description' or 'list_price' or 'taxes_id' or 'categ_id' or 'default_code' or 'barcode' or 'l10n_pe_edi_unspsc' or 'company_id' or 'attribute_line_ids' or 'purchase_requisition' or 'supplier_taxes_id' or 'purchase_method' or 'description_purchase' or 'description_sale' or 'sale_line_warn' or 'property_stock_production' or 'property_stock_inventory' or 'responsible_id' or 'weight' or 'volume' or 'produce_delay' or 'sale_delay' or 'packaging_ids' or 'description_pickingin' or 'description_picking' or 'description_pickingout' or 'property_account_income_id' or 'property_account_expense_id' or 'asset_category_id' or 'property_account_creditor_price_difference' or 'service_to_purchase' or 'is_landed_cost' in vals:
            if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
                t = super(product_template,self).write(vals)
                return t
            else:
                raise UserError("No Tiene Los Permisos de 'Manejo Creacion de Productos p'" + str(vals))
        else:
            t = super(product_template,self).write(vals)
            return t
            

class product_product(models.Model):
    _inherit = 'product.product'
    
    def unlink(self):
        if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
            t = super(product_product,self).unlink()
            return t
        else:
            raise UserError("No Tiene Los Permisos de 'Manejo Creacion de Productos'")

    @api.model
    def create(self,vals):
        if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
            t = super(product_product,self).create(vals)
            return t
        else:
            raise UserError("No Tiene Los Permisos de 'Manejo Creacion de Productos'")
           
    def write(self,vals):
        if 'seller_ids' or 'name' or 'route_ids' or 'sale_ok' or 'purchase_ok' or 'detailed_type' or 'invoice_policy' or 'expense_policy' or 'uom_id' or 'uom_po_id' or 'description' or 'list_price' or 'taxes_id' or 'categ_id' or 'default_code' or 'barcode' or 'l10n_pe_edi_unspsc' or 'company_id' or 'attribute_line_ids' or 'purchase_requisition' or 'supplier_taxes_id' or 'purchase_method' or 'description_purchase' or 'description_sale' or 'sale_line_warn' or 'property_stock_production' or 'property_stock_inventory' or 'responsible_id' or 'weight' or 'volume' or 'produce_delay' or 'sale_delay' or 'packaging_ids' or 'description_pickingin' or 'description_picking' or 'description_pickingout' or 'property_account_income_id' or 'property_account_expense_id' or 'asset_category_id' or 'property_account_creditor_price_difference' or 'service_to_purchase' or 'is_landed_cost' in vals:
            if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
                t = super(product_product,self).write(vals)
                return t
            else:
                raise UserError("No Tiene Los Permisos de 'Manejo Creacion de Productos v'" + str(vals))
        else:
            t = super(product_product,self).write(vals)
            return t
            





class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if line.product_id and partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
                # Convert the price in the right currency.
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                price = self.currency_id._convert(line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                    default_uom = line.product_id.product_tmpl_id.uom_po_id
                    price = line.product_uom._compute_price(price, default_uom)

                supplierinfo = self._prepare_supplier_info(partner, line, price, currency)
                # In case the order partner is a contact address, a new supplierinfo is created on
                # the parent company. In this case, we keep the product name and code.
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom)
                if seller:
                    supplierinfo['product_name'] = seller.product_name
                    supplierinfo['product_code'] = seller.product_code
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    if self.env.user.has_group("product_template_restriction.group_product_template_restriction"):
                        line.product_id.write(vals)
                    else:
                        grupo_editor = self.env.ref('product_template_restriction.group_product_template_restriction')
                        grupo_editor.sudo().write({'users':[(4, self.env.user.id)]
                                                   })
                        line.product_id.write(vals)
                        grupo_editor.sudo().write({'users':[(3, self.env.user.id)]
                                                   })
                        
                except AccessError:  # no write access rights -> just ignore
                    break






#def button_validate(self):
        ## Clean-up the context key at validation to avoid forcing the creation of immediate
        ## transfers.
        #ctx = dict(self.env.context)
        #ctx.pop('default_immediate_transfer', None)
        #self = self.with_context(ctx)

        ## Sanity checks.
        #pickings_without_moves = self.browse()
        #pickings_without_quantities = self.browse()
        #pickings_without_lots = self.browse()
        #products_without_lots = self.env['product.product']
        #for picking in self:
            #if not picking.move_lines and not picking.move_line_ids:
                #pickings_without_moves |= picking

            #picking.message_subscribe([self.env.user.partner_id.id])
            #picking_type = picking.picking_type_id
            #precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            #no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            #no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            #if no_reserved_quantities and no_quantities_done:
                #pickings_without_quantities |= picking

            #if picking_type.use_create_lots or picking_type.use_existing_lots:
                #lines_to_check = picking.move_line_ids
                #if not no_quantities_done:
                    #lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                #for line in lines_to_check:
                    #product = line.product_id
                    #if product and product.tracking != 'none':
                        #if not line.lot_name and not line.lot_id:
                            #pickings_without_lots |= picking
                            #products_without_lots |= product

        #if not self._should_show_transfers():
            #if pickings_without_moves:
                #raise UserError(_('Please add some items to move.'))
            #if pickings_without_quantities:
                #raise UserError(self._get_without_quantities_error_message())
            #if pickings_without_lots:
                #raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
        #else:
            #message = ""
            #if pickings_without_moves:
                #message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            #if pickings_without_quantities:
                #message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            #if pickings_without_lots:
                #message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
            #if message:
                #raise UserError(message.lstrip())
            
            
 
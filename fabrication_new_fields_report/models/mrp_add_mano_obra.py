
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models
from odoo.tools import float_round
from odoo import fields, models , api , _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
class workforce_name(models.Model):
    _name = 'workforce.name'
    _description = "mano de obra nombre"
    name = fields.Char(string = "Mano De Obra")


class stock_move(models.Model):
    _inherit = 'stock.move'
    
    costo_produccion_unitario_calculado = fields.Float(string = "Costo Produccion Calculado", compute="get_costo_calculado")
    costo_produccion_total_calculado = fields.Float(string = "Costo Produccion Total Calculado", compute="get_costo_calculado")
    def get_costo_calculado(self):
        for i in self:
            i.costo_produccion_unitario_calculado = 0
            i.costo_produccion_total_calculado = 0
            relacion = i.env['stock.valuation.layer'].sudo().search([('stock_move_id', '=', i.id)])
            if len(relacion)>0:
                i.costo_produccion_unitario_calculado = abs(relacion.unit_cost)
                i.costo_produccion_total_calculado = abs(relacion.value)



class workforce_cost(models.Model):
    _name = 'workforce.cost'
    _description = "mano de obra"
    name = fields.Many2one("workforce.name", string = "Mano De Obra")
    empleado_id = fields.Many2one("hr.employee", string="Empleado")
    horas = fields.Float(string = "Horas")
    costo_unitario = fields.Float(string = "Costo Unitario")
    costo_total = fields.Float(string = "Costo Total", compute="get_costo_total")
    production_id = fields.Many2one('mrp.production', string="Orden De Produccion")

    def get_costo_total(self):
        for i in self:
            i.costo_total = i.costo_unitario * i.horas


class mrp_production(models.Model):
    _inherit = 'mrp.production'
    workforce_ids = fields.One2many('workforce.cost', 'production_id', string='Mano De Obra')

    def button_mark_done(self):
        t = super(mrp_production,self).button_mark_done()
        for i in self:
            total = 0
            stock_moves = self.env['stock.move.line'].sudo().search([('move_id.production_id', '=', i.id)])
            if len(stock_moves)>0:
                diccionario = self.env['report.mrp_account_enterprise.mrp_cost_structure'].get_lines(i)
                if diccionario:
                    for dicts in diccionario:
                        if 'total_cost' in dicts:
                            total += dicts['total_cost']
                        if 'operations' in dicts:
                            for m in dicts['operations']:
                                total += m[3] * m[4]
                if len(i.workforce_ids)>0:
                    for w in i.workforce_ids:
                        total += w.costo_total

                #mo_qty = 0
                #uom = i.product_id.uom_id
                #qty = i.product_qty
                #if i.product_uom_id.id == uom.id:
                    #mo_qty += qty
                #else:
                    #mo_qty += i.product_uom_id._compute_quantity(qty, uom)
                moves_moves = []
                for moves in stock_moves:
                    moves.move_id.sudo().price_unit_it = total / i.product_qty
                    if moves.move_id in moves_moves:
                        pass
                    else:
                        moves_moves.append(moves.move_id)
                for m in moves_moves:                
                    line_val = self.env['stock.valuation.layer'].search([('product_id','=',m.product_id.id),('stock_move_id','=',m.id)])
                    if len(line_val)>0:
                        line_val.unit_cost = m.price_unit_it
                        line_val.value = m.price_unit_it * line_val.quantity
                    else:
                        data = {
                            'product_id':m.product_id.id,
                            'unit_cost':m.price_unit_it,
                            'quantity':m.product_uom_qty,
                            'value':m.price_unit_it*m.product_uom_qty,
                            'company_id':i.company_id.id,
                            'stock_move_id':m.id,
                        }
                        line_val = self.env['stock.valuation.layer'].create(data)

                    costo_actual = 0
                    cantidad_actual = 0
                    for ij in self.env['stock.valuation.layer'].search([('product_id','=',m.product_id.id)]):
                        costo_actual += ij.value
                        cantidad_actual += ij.quantity	
                    self.env.cr.execute("""
                        select id from ir_property 
                        where name = 'standard_price' and company_id = """ + str(self.env.company.id)+ """ and res_id = 'product.product,"""+str(m.product_id.id)+"""' 
                        """) 
                    ver = self.env.cr.fetchall()
                    if len(ver)==0:
                        self.env['ir.property'].create({
                            'name':'standard_price',
                            'company_id':i.company_id.id,
                            'res_id':'product.product,'+str(m.product_id.id),
                            'value_float':costo_actual / cantidad_actual if cantidad_actual!=0 else 0,
                            'type':'float',
                            'fields_id': (self.env['ir.model.fields'].sudo().search([('name','=','standard_price'),('model_id','=',self.env['ir.model'].sudo().search([('model','=','product.product')]).id)])).id,
                            })
                    else:
                        self.env.cr.execute("""
                        update ir_property set value_float = """ + str(costo_actual / cantidad_actual if cantidad_actual!=0 else 0) + """
                        where name = 'standard_price' and company_id = """ + str(self.env.company.id)+ """ and res_id = 'product.product,"""+str(m.product_id.id)+"""' 
                        """) 
        return t





class MrpCostStructure(models.AbstractModel):
    _inherit = 'report.mrp_account_enterprise.mrp_cost_structure'

    def get_lines(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        currency_table = self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}})
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0
            # variables to calc cost share (i.e. between products/byproducts) since MOs can have varying distributions
            total_cost_by_mo = defaultdict(float)
            component_cost_by_mo = defaultdict(float)
            operation_cost_by_mo = defaultdict(float)

            # Get operations details + cost
            operations = []
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                query_str = """SELECT
                                    wo.production_id,
                                    wo.id,
                                    op.id,
                                    wo.name,
                                    partner.name,
                                    sum(t.duration),
                                    CASE WHEN wo.costs_hour = 0.0 THEN wc.costs_hour ELSE wo.costs_hour END AS costs_hour,
                                    currency_table.rate
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder wo ON (wo.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id)
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (wo.operation_id = op.id)
                                LEFT JOIN {currency_table} ON currency_table.company_id = t.company_id
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY wo.production_id, wo.id, op.id, wo.name, wc.costs_hour, partner.name, t.user_id, currency_table.rate
                                ORDER BY wo.name, partner.name
                            """.format(currency_table=currency_table,)
                self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
                for mo_id, dummy_wo_id, op_id, wo_name, user, duration, cost_hour, currency_rate in self.env.cr.fetchall():
                    cost = duration / 60.0 * cost_hour * currency_rate
                    total_cost_by_mo[mo_id] += cost
                    operation_cost_by_mo[mo_id] += cost
                    operations.append([user, op_id, wo_name, duration / 60.0, cost_hour * currency_rate])

            # Get the cost of raw material effectively used
            raw_material_moves = []
            query_str = """SELECT
                                sm.product_id,
                                mo.id,
                                abs(SUM(sm.product_uom_qty)),
                                abs(SUM(sm.product_uom_qty*sm.price_unit_it)),
                                currency_table.rate
                             FROM stock_move AS sm
                       LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
                       LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                            WHERE sm.raw_material_production_id in %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                         GROUP BY sm.product_id, mo.id, currency_table.rate""".format(currency_table=currency_table,)
            self.env.cr.execute(query_str, (tuple(mos.ids), ))
            for product_id, mo_id, qty, cost, currency_rate in self.env.cr.fetchall():
                cost *= currency_rate
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                })
                total_cost_by_mo[mo_id] += cost
                component_cost_by_mo[mo_id] += cost
                total_cost += cost

            # Get the cost of scrapped materials
            scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])
            mano_d_obra = self.env['workforce.cost'].sudo().search([('id', 'in', mos.workforce_ids.ids)])

            # Get the byproducts and their total + avg per uom cost share amounts
            total_cost_by_product = defaultdict(float)
            qty_by_byproduct = defaultdict(float)
            qty_by_byproduct_w_costshare = defaultdict(float)
            component_cost_by_product = defaultdict(float)
            operation_cost_by_product = defaultdict(float)
            # tracking consistent uom usage across each byproduct when not using byproduct's product uom is too much of a pain
            # => calculate byproduct qtys/cost in same uom + cost shares (they are MO dependent)
            byproduct_moves = mos.move_byproduct_ids.filtered(lambda m: m.state != 'cancel')
            for move in byproduct_moves:
                qty_by_byproduct[move.product_id] += move.product_qty
                # byproducts w/o cost share shouldn't be included in cost breakdown
                if move.cost_share != 0:
                    qty_by_byproduct_w_costshare[move.product_id] += move.product_qty
                    cost_share = move.cost_share / 100
                    total_cost_by_product[move.product_id] += total_cost_by_mo[move.production_id.id] * cost_share
                    component_cost_by_product[move.product_id] += component_cost_by_mo[move.production_id.id] * cost_share
                    operation_cost_by_product[move.product_id] += operation_cost_by_mo[move.production_id.id] * cost_share

            # Get product qty and its relative total + avg per uom cost share amount
            uom = product.uom_id
            mo_qty = 0
            for m in mos:
                cost_share = float_round(1 - sum(m.move_finished_ids.mapped('cost_share')) / 100, precision_rounding=0.0001)
                total_cost_by_product[product] += total_cost_by_mo[m.id] * cost_share
                component_cost_by_product[product] += component_cost_by_mo[m.id] * cost_share
                operation_cost_by_product[product] += operation_cost_by_mo[m.id] * cost_share
                qty = sum(m.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped('product_uom_qty'))
                if m.product_uom_id.id == uom.id:
                    mo_qty += qty
                else:
                    mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'currency': self.env.company.currency_id,
                'raw_material_moves': raw_material_moves,
                'total_cost': total_cost,
                'scraps': scraps,
                'mocount': len(mos),
                'byproduct_moves': byproduct_moves,
                'component_cost_by_product': component_cost_by_product,
                'operation_cost_by_product': operation_cost_by_product,
                'man_de_obra': mano_d_obra,
                'qty_by_byproduct': qty_by_byproduct,
                'qty_by_byproduct_w_costshare': qty_by_byproduct_w_costshare,
                'total_cost_by_product': total_cost_by_product
            })
        return res


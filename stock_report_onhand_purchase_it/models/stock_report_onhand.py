# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class stock_move(models.Model):
	_inherit = 'stock.move'

	def show_picking_purchase(self):
		aids=[self.picking_id.id]
		return {
			'name': u'Transferencia',
			'type': 'ir.actions.act_window',
			'res_model': 'stock.picking',
			'view_mode': 'form',
			'res_id':self.picking_id.id,
			'views': [(self.env.ref('stock.view_picking_form').id, 'form')],
		}		


class StockReportOnhandPurchase(models.Model):
	_name = 'stock.report.onhand.purchase'
	_description = 'BackOrder Compras'
	_auto = False

	complete_name = fields.Char(u'Ubicación')
	product_id = fields.Many2one('product.product','Producto')
	name_product = fields.Char(u'Producto')
	default_code = fields.Char(u'Código')
	cantidad = fields.Float(string='BackOrder', digits=(12,2))
	parent_path = fields.Char(u'Ruta Ubicación')
	cantidad_unidad = fields.Float('Cantidad unidad')
	stock_actual = fields.Float('Stock Actual')

	def show_moves(self):
		cadsql = """
			select  
			distinct stock_move.id
			from stock_move 
			inner join stock_location origen on stock_move.location_id = origen.id
			inner join stock_location destino on stock_move.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where state not in ('draft','cancel','done') and purchase_line_id is not null
			and origen.id != destino.id and pt.type= 'product'
			and stock_move.product_id = %d
			and destino.complete_name = '%s'
		"""%(self.product_id.id,self.complete_name)
		print(cadsql)
		self.env.cr.execute(cadsql)
		data = self.env.cr.dictfetchall()
		aids=[]
		for l in data:
			aids.append(l['id'])
		return {
			'name': u'Movimientos de Almacén',
			'type': 'ir.actions.act_window',
			'res_model': 'stock.move',
			'view_mode': 'tree,form',
			'domain':[('id','in',aids)],
			'views': [(self.env.ref('stock_report_onhand_purchase_it.view_stock_move_report_onhand_purchase_tree').id, 'tree')],
		}


	def init(self):
		tools.drop_view_if_exists(self._cr, 'stock_report_onhand_purchase')
		query = """
			CREATE or REPLACE VIEW stock_report_onhand_purchase AS (
			--tranferido
select 
row_number() OVER () AS id,
			product_id,
			pt.name as name_product,
			pp.default_code,
			sum(cantidad) as cantidad,
			sum(cantidad_comprada) as stock_actual,
			sum(cantidad_unidad) as cantidad_unidad,
			parent_path,
			complete_name
			from
			(
			select  
			stock_move.product_id,
			stock_move.name as ú,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*0 as cantidad,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*1 as cantidad_comprada,
			sum(stock_move.product_uom_qty) as cantidad_unidad,
			stock_move.picking_type_id,
			stock_move.warehouse_id as almacen,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			from stock_move 
			inner join stock_move_line on stock_move.id = stock_move_line.move_id
			inner join stock_location origen on stock_move_line.location_id = origen.id
			inner join stock_location destino on stock_move_line.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where stock_move.state in ('done') 
			and origen.id != destino.id and pt.type= 'product'
			and destino.usage='internal' 
			and sale_line_id is null
			and purchase_line_id is null
			group by 
			stock_move.product_id,
			stock_move.name,
			stock_move.picking_type_id,
			stock_move.warehouse_id,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			union all
			
			select  
			stock_move.product_id,
			stock_move.name as producto,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*0 as cantidad,
			
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*-1 as cantidad_comprada,
			sum(stock_move.product_uom_qty)*-1 as cantidad_unidad,
			stock_move.picking_type_id,
			stock_move.warehouse_id as almacen,
			origen.parent_path,
			origen.complete_name,
			stock_move.product_uom
			from stock_move 
			inner join stock_move_line on stock_move.id = stock_move_line.move_id
			inner join stock_location origen on stock_move_line.location_id = origen.id
			inner join stock_location destino on stock_move_line.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where stock_move.state in ('done') 
			and origen.id != destino.id and pt.type= 'product'
			and origen.usage='internal' and sale_line_id is null
			and purchase_line_id is null
			group by 
			stock_move.product_id,
			stock_move.name,
			stock_move.picking_type_id,
			stock_move.warehouse_id,
			origen.parent_path,
			origen.complete_name,
			stock_move.product_uom
			union all

			--comprado solo concretadas
			select  
			stock_move.product_id,
			stock_move.name as producto,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*0 as cantidad,
			
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*1 as cantidad_comprada,
			0 as cantidad_unidad,
			stock_move.picking_type_id,
			stock_move.warehouse_id as almacen,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			from stock_move 
			inner join stock_move_line on stock_move.id = stock_move_line.move_id
			inner join stock_location origen on stock_move_line.location_id = origen.id
			inner join stock_location destino on stock_move_line.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where stock_move_line.state in ('done') and purchase_line_id is not null
			and origen.id != destino.id and pt.type= 'product'
			group by 
			stock_move.product_id,
			stock_move.name,
			stock_move.picking_type_id,
			stock_move.warehouse_id,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			union all
			--comprado
			select  
			stock_move.product_id,
			stock_move.name as producto,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move.product_qty::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move.product_uom_qty
			END)*1 as cantidad,
			0 as cantidad_comprada,
			sum(stock_move.product_uom_qty) as cantidad_unidad,
			stock_move.picking_type_id,
			stock_move.warehouse_id as almacen,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			from stock_move 
			inner join stock_location origen on stock_move.location_id = origen.id
			inner join stock_location destino on stock_move.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where state not in ('draft','cancel','done') and purchase_line_id is not null
			and origen.id != destino.id and pt.type= 'product'
			group by 
			stock_move.product_id,
			stock_move.name,
			stock_move.picking_type_id,
			stock_move.warehouse_id,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			-- vendidos devueltos
			union all
			select  
			stock_move.product_id,
			stock_move.name as producto,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*0 as cantidad,
			
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*1 as cantidad_comprada,
			sum(stock_move.product_uom_qty) as cantidad_unidad,
			stock_move.picking_type_id,
			stock_move.warehouse_id as almacen,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
			
			from stock_move 
			inner join stock_move_line on stock_move.id = stock_move_line.move_id
			inner join stock_location origen on stock_move_line.location_id = origen.id
			inner join stock_location destino on stock_move_line.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where stock_move.state in ('done') and stock_move.sale_line_id is not null and pt.type= 'product'
			and origen.id != destino.id
			and destino.usage='internal'
			group by 
			stock_move.product_id,
			stock_move.name,
			stock_move.picking_type_id,
			stock_move.warehouse_id,
			destino.parent_path,
			destino.complete_name,
			stock_move.product_uom
	
	
			--VENDIDOS
			union all
			select  
			stock_move.product_id,
			stock_move.name as producto,
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*0 as cantidad,
			
			sum(CASE
				WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
				ELSE stock_move_line.qty_done
			END)*-1 as cantidad_comprada,
			sum(stock_move.product_uom_qty) as cantidad_unidad,
			stock_move.picking_type_id,
			stock_move.warehouse_id as almacen,
			origen.parent_path,
			origen.complete_name,
			stock_move.product_uom
			
			from stock_move 
			inner join stock_move_line on stock_move.id = stock_move_line.move_id
			inner join stock_location origen on stock_move_line.location_id = origen.id
			inner join stock_location destino on stock_move_line.location_dest_id = destino.id
			LEFT JOIN product_product pp on pp.id=stock_move.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			
			JOIN uom_uom ON stock_move.product_uom = uom_uom.id
			JOIN uom_uom uomt ON uomt.id = pt.uom_id
			where stock_move.state in ('done') and stock_move.sale_line_id is not null and pt.type= 'product'
			and origen.id != destino.id
			and origen.usage='internal'
			group by 
			stock_move.product_id,
			stock_move.name,
			stock_move.picking_type_id,
			stock_move.warehouse_id,
			origen.parent_path,
			origen.complete_name,
			stock_move.product_uom
			) o
			LEFT JOIN product_product pp on pp.id=o.product_id
			LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			group by product_id,
			pp.default_code,
			pt.name,
			parent_path,
			complete_name
			order by product_id);"""
		self.env.cr.execute(query)


	# def init(self):
	# 	tools.drop_view_if_exists(self._cr, 'stock_report_onhand')
	# 	query = """
	# 		CREATE or REPLACE VIEW stock_report_onhand_purchase AS (
	# 		--tranferido
	# 		select 
	# 		row_number() OVER () AS id,
	# 		product_id,
	# 		pt.name as name_product,
	# 		pp.default_code,
	# 		sum(cantidad) as cantidad,
	# 		sum(cantidad_comprada) as stock_actual,
	# 		sum(cantidad_unidad) as cantidad_unidad,
	# 		parent_path,
	# 		complete_name, 
	# 		empaque.name as presentacion
	# 		from
	# 		(
	# 		select  
	# 		stock_move.product_id,
	# 		stock_move.name as producto,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END) as cantidad,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END) as cantidad_comprada,
	# 		sum(stock_move.product_uom_qty) as cantidad_unidad,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id as almacen,
	# 		destino.parent_path,
	# 		destino.complete_name,
	# 		stock_move.product_uom
	# 		from stock_move 
	# 		inner join stock_move_line on stock_move.id = stock_move_line.move_id
	# 		inner join stock_location origen on stock_move_line.location_id = origen.id
	# 		inner join stock_location destino on stock_move_line.location_dest_id = destino.id
	# 		LEFT JOIN product_product pp on pp.id=stock_move.product_id
	# 		LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
	# 		JOIN uom_uom ON stock_move.product_uom = uom_uom.id
	# 		JOIN uom_uom uomt ON uomt.id = pt.uom_id
	# 		where stock_move.state in ('done') 
	# 		and origen.id != destino.id and pt.type= 'product'
	# 		and destino.usage='internal' 
	# 		and sale_line_id is null
	# 		and purchase_line_id is null
	# 		group by 
	# 		stock_move.product_id,
	# 		stock_move.name,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id,
	# 		destino.parent_path,
	# 		destino.complete_name,
	# 		stock_move.product_uom
	# 		union all
	# 		--comprados esperando
	# 		select  
	# 		stock_move.product_id,
	# 		stock_move.name as producto,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END) *-1 as cantidad,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END) *-1 as cantidad_comprada,
	# 		sum(stock_move.product_uom_qty)*-1 as cantidad_unidad,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id as almacen,
	# 		origen.parent_path,
	# 		origen.complete_name,
	# 		stock_move.product_uom
	# 		from stock_move 
	# 		inner join stock_move_line on stock_move.id = stock_move_line.move_id
	# 		inner join stock_location origen on stock_move_line.location_id = origen.id
	# 		inner join stock_location destino on stock_move_line.location_dest_id = destino.id
	# 		LEFT JOIN product_product pp on pp.id=stock_move.product_id
	# 		LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			
	# 		JOIN uom_uom ON stock_move.product_uom = uom_uom.id
	# 		JOIN uom_uom uomt ON uomt.id = pt.uom_id
	# 		where stock_move.state in ('done') 
	# 		and origen.id != destino.id and pt.type= 'product'
	# 		and origen.usage='internal' and purchase_line_id is null
	# 		and purchase_line_id is null
	# 		group by 
	# 		stock_move.product_id,
	# 		stock_move.name,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id,
	# 		origen.parent_path,
	# 		origen.complete_name,
	# 		stock_move.product_uom
	# 		union all

	# 		--comprado completos
	# 		select  
	# 		stock_move.product_id,
	# 		stock_move.name as producto,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END)*1 as cantidad,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END)*1 as cantidad_comprada,
	# 		0 as cantidad_unidad,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id as almacen,
	# 		origen.parent_path,
	# 		origen.complete_name,
	# 		stock_move.product_uom
	# 		from stock_move 
	# 		inner join stock_move_line on stock_move.id = stock_move_line.move_id
	# 		inner join stock_location origen on stock_move_line.location_id = origen.id
	# 		inner join stock_location destino on stock_move_line.location_dest_id = destino.id
	# 		LEFT JOIN product_product pp on pp.id=stock_move.product_id
	# 		LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
	# 		JOIN uom_uom ON stock_move.product_uom = uom_uom.id
	# 		JOIN uom_uom uomt ON uomt.id = pt.uom_id
	# 		where stock_move_line.state in ('done') and purchase_line_id is not null
	# 		and origen.id != destino.id and pt.type= 'product'
	# 		group by 
	# 		stock_move.product_id,
	# 		stock_move.name,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id,
	# 		origen.parent_path,
	# 		origen.complete_name,
	# 		stock_move.product_uom
	# 		union all
	# 		--comprado pendiente
	# 		select  
	# 		stock_move.product_id,
	# 		stock_move.name as producto,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move.product_qty::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move.product_uom_qty
	# 		END)*1 as cantidad,
	# 		0 as cantidad_comprada,
	# 		sum(stock_move.product_uom_qty)*-1 as cantidad_unidad,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id as almacen,
	# 		origen.parent_path,
	# 		origen.complete_name,
	# 		stock_move.product_uom
	# 		from stock_move 
	# 		inner join stock_location origen on stock_move.location_id = origen.id
	# 		inner join stock_location destino on stock_move.location_dest_id = destino.id
	# 		LEFT JOIN product_product pp on pp.id=stock_move.product_id
	# 		LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
	# 		JOIN uom_uom ON stock_move.product_uom = uom_uom.id
	# 		JOIN uom_uom uomt ON uomt.id = pt.uom_id
	# 		where state not in ('draft','cancel','done') and purchase_line_id is not null
	# 		and origen.id != destino.id and pt.type= 'product'
	# 		group by 
	# 		stock_move.product_id,
	# 		stock_move.name,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id,
	# 		origen.parent_path,
	# 		origen.complete_name,
	# 		stock_move.product_uom

	# 		--VENDIDOS
	# 		union all
	# 		select  
	# 		stock_move.product_id,
	# 		stock_move.name as producto,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END)*-1 as cantidad,
	# 		sum(CASE
	# 			WHEN uom_uom.id <> uomt.id THEN round((stock_move_line.qty_done::double precision * uomt.factor::double precision / uom_uom.factor::double precision)::numeric, 6)
	# 			ELSE stock_move_line.qty_done
	# 		END)*-1 as cantidad_comprada,
	# 		sum(stock_move.product_uom_qty)*-1 as cantidad_unidad,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id as almacen,
	# 		destino.parent_path,
	# 		destino.complete_name,
	# 		stock_move.product_uom
	# 		from stock_move 
	# 		inner join stock_move_line on stock_move.id = stock_move_line.move_id
	# 		inner join stock_location origen on stock_move_line.location_id = origen.id
	# 		inner join stock_location destino on stock_move_line.location_dest_id = destino.id
	# 		LEFT JOIN product_product pp on pp.id=stock_move.product_id
	# 		LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
			
	# 		JOIN uom_uom ON stock_move.product_uom = uom_uom.id
	# 		JOIN uom_uom uomt ON uomt.id = pt.uom_id
	# 		where stock_move.state in ('done') and stock_move.sale_line_id is not null and pt.type= 'product'
	# 		and origen.id != destino.id
	# 		group by 
	# 		stock_move.product_id,
	# 		stock_move.name,
	# 		stock_move.picking_type_id,
	# 		stock_move.warehouse_id,
	# 		destino.parent_path,
	# 		destino.complete_name,
	# 		stock_move.product_uom
	# 		) o
	# 		LEFT JOIN product_product pp on pp.id=o.product_id
	# 		LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
	# 		left join empaque on pt.empaque = empaque.id
	# 		group by product_id,
	# 		pp.default_code,
	# 		pt.name,
	# 		parent_path,
	# 		complete_name, empaque.name
	# 		order by product_id);"""
	# 	self.env.cr.execute(query)

# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError
import codecs

values = {}

class wizard_get_quants(models.Model):
	_name = "wizard.get.quants"
	name = fields.Many2one('res.company',string=u'Compañia',required=True, default=lambda self: self.env.company,readonly=True)
	check_detail = fields.Boolean("Informe De Saldos Detallado", default=False)

	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()

		#direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(output, {'constant_memory': False})
		worksheet = workbook.add_worksheet("REPORTE DE SALDOS")
		x= 9

		worksheet.set_column('A:A', 12.80)
		worksheet.set_column('B:B', 18.33)
		worksheet.set_column('C:C', 50)
		worksheet.set_column('D:D', 25)
		worksheet.set_column('E:E', 12.80)
		worksheet.set_column('F:F', 25)
		worksheet.set_column('G:G', 12.80)
		worksheet.set_column('H:H', 12.80)
		worksheet.set_column('I:I', 12.80)
		worksheet.set_column('J:J', 25)
		worksheet.set_column('K:K', 20)
		worksheet.set_column('L:L', 12.80)
		
		cell_titulo = workbook.add_format({'bold': True})
		cell_titulo.set_align('center')
		cell_titulo.set_border(2)
		cell_titulo.set_font_name('Calibri')
		cell_titulo.set_font_size(14)
		cell_titulo.set_bg_color('#F1F4FB')

		cell_r = workbook.add_format({'bold': True})
		cell_r.set_align('center')
		cell_r.set_border(2)
		cell_r.set_font_name('Calibri')
		cell_r.set_font_size(12)
		cell_r.set_bg_color('#F1F4FB')	

		cell_n = workbook.add_format({'bold': False})
		cell_n.set_align('left')
		cell_n.set_border(1)
		cell_n.set_font_name('Calibri')
		cell_n.set_font_size(11)
	
		cell_right = workbook.add_format({'bold': True})
		cell_right.set_align('right')
		cell_right.set_border(1)
		cell_right.set_font_name('Calibri')
		cell_right.set_font_size(11)
		cell_right.set_num_format('##0.00')
		
		cell_right_soles = workbook.add_format({'bold': True})
		cell_right_soles.set_align('right')
		cell_right_soles.set_border(1)
		cell_right_soles.set_font_name('Calibri')
		cell_right_soles.set_font_size(11)
		cell_right_soles.set_num_format(11)
		cell_right_soles.set_num_format('"S/" #,##0.00;"S/" -#,##0.00')

		cell_right_dolares = workbook.add_format({'bold': True})
		cell_right_dolares.set_align('right')
		cell_right_dolares.set_border(1)
		cell_right_dolares.set_font_name('Calibri')
		cell_right_dolares.set_font_size(11)
		cell_right_dolares.set_num_format('$ #,##0.00;$ -#,##0.00')


		cell_right_n = workbook.add_format({'bold': False})
		cell_right_n.set_align('right')
		cell_right_n.set_border(1)
		cell_right_n.set_font_name('Calibri')
		cell_right_n.set_font_size(11)
		cell_right_n.set_num_format('##0.00')

		cell_numero = workbook.add_format({'bold': False})
		cell_numero.set_align('right')
		cell_numero.set_border(1)
		cell_numero.set_font_name('Calibri')
		cell_numero.set_font_size(11)
		cell_numero.set_num_format('"S/" #,##0.00;"S/" -#,##0.00')
		
		cell_porcentaje = workbook.add_format({'bold': False})
		cell_porcentaje.set_align('right')
		cell_porcentaje.set_border(1)
		cell_porcentaje.set_font_name('Calibri')
		cell_porcentaje.set_font_size(11)
		cell_porcentaje.set_num_format('"%" #,##0.00;"%" -#,##0.00')

		cell_numero_dolar = workbook.add_format({'bold': False})
		cell_numero_dolar.set_align('right')
		cell_numero_dolar.set_border(1)
		cell_numero_dolar.set_font_name('Calibri')
		cell_numero_dolar.set_font_size(11)
		cell_numero_dolar.set_num_format('$ #,##0.00;$ -#,##0.00')

		import datetime
		from datetime import timedelta
		worksheet.merge_range(1,0,2,10, "REPORTE DE SALDOS", cell_titulo)

		worksheet.set_row(4, 28.20)
		worksheet.set_row(5, 28.20)
		worksheet.write(4,0, "Fecha:", cell_r)
		worksheet.write(4,1, str((datetime.datetime.now()-timedelta(hours=5)).date()), cell_r)


		worksheet.merge_range('A6:C6', "Articulos", cell_r)
		worksheet.write(6,0, "Secuencia", cell_r)
		worksheet.write(6,1, "Ref Interna", cell_r)
		worksheet.write(6,2, "Producto", cell_r)
		worksheet.merge_range('D6:D7', "Saldos S/", cell_r)
		worksheet.merge_range('E6:E7', "% Soles", cell_r)
		worksheet.merge_range('F6:F7', "Saldo USD $", cell_r)
		worksheet.merge_range('G6:G7', "% Dolares", cell_r)
		worksheet.merge_range('H6:H7', "Valor Unit S/", cell_r)
		worksheet.merge_range('I6:I7', "Valor Unit $", cell_r)
		worksheet.merge_range('J6:J7', "Saldo Cantidad", cell_r)
		worksheet.merge_range('K6:K7', "Lote/Nro Serie", cell_r)
		worksheet.merge_range('L6:L7', "Ubicación/Almacen", cell_r)

		columna = 7
		contador = 1
		total_soles = 0
		total_dolares = 0
		import datetime
		from datetime import timedelta
		if self.check_detail == False:
			self.env.cr.execute("""select quant.quantity as cantidad, product.default_code as default_code, product.name as nombre_producto,
					prop.value_float as precio_unitario, spl.name as lote, sl.name as ubicacion
					from stock_quant quant
					left join product_product product on product.id = stock_quant.product_id
					left join ir_property prop on prop.res_id = 'product.product,' || product.id
					left join stock_production_lot spl on spl.id = quant.lot_id
					left join stock_location sl on sl.id = quant.location_id
					where sl.usage = 'internal' and quant.company_id = """+str(self.env.company.id)+"""; """)
			cnslta = self.env.cr.dictfetchall()
			tipo_cambio = self.env['res.currency.rate'].sudo().search([('name','=',(datetime.datetime.now()-timedelta(hours=5)).date()),('currency_id.name','=','USD')], limit=1)
			if len(tipo_cambio)>0:
				tasa_cambio = tipo_cambio[0].sale_type
			for x in cnslta:
				#los totales si se hacen desde la consulta son muchas variables q no funcionaran como prod con costo 0 o servicio almacenable
				total_soles += x['cantidad'] * x['precio_unitario']
			total_dolares = (total_soles/tasa_cambio) if tasa_cambio != 0 else 0
			for i in total_quants:
				worksheet.write(columna,0, str(contador),cell_n)
				worksheet.write(columna,1, str(x['default_code'] if x['default_code'] else ''),cell_n)
				worksheet.write(columna,2, str(x['nombre_producto'] if x['nombre_producto'] else ''),cell_n)
				worksheet.write(columna,3, x['cantidad'] * x['precio_unitario'],cell_numero)
				
				worksheet.write(columna,4, (((x['cantidad'] * x['precio_unitario'])*100)/total_soles) if total_soles!=0 else 0  ,cell_porcentaje)
				if tasa_cambio != 0:
					worksheet.write(columna,5, (x['cantidaad'] * x['precio_unitario'])/tasa_cambio,cell_numero_dolar)
					worksheet.write(columna,8, x['precio_unitario']/tasa_cambio,cell_numero_dolar)
					worksheet.write(columna,6, ((((x['cantidad'] * x['precio_unitario'])/tasa_cambio)*100)/total_dolares) if total_dolares != 0 else 0,cell_porcentaje)
				else:
					worksheet.write(columna,5, 0,cell_numero_dolar)
					worksheet.write(columna,6, 0,cell_porcentaje)
					worksheet.write(columna,8, 0,cell_numero_dolar)
				
				worksheet.write(columna,7, x['precio_unitario'] if x['precio_unitario'] else 0,cell_numero)

				worksheet.write(columna,9, x['cantidad'] if x['cantidad'] else 0,cell_right_n)
				worksheet.write(columna,10, str(x['lote'] if x['lote'] else ''),cell_n)
				worksheet.write(columna,11, str(x['ubicacion'] if x['ubicacion'] else ''),cell_n)
				contador = contador+1
				columna = columna+1
				
			worksheet.write(columna,2, "Total S/",cell_right)
			worksheet.write(columna,3, total_soles,cell_right_soles)
			worksheet.write(columna,4, "Total $",cell_right)
			worksheet.write(columna,5, total_dolares,cell_right_dolares)
			workbook.close()
			output.seek(0)

			attach_id = self.env['ir.attachment'].create({
						'name': "Reporte De Saldos Detallado.xlsx",
						'type': 'binary',
						'datas': base64.encodestring(output.read()),
						'eliminar_automatico': True
					})
			output.close()


			return {
				'type': 'ir.actions.client',
				'tag': 'notification_llikha',
				'params': {
					'title':'Reporte De Saldos Detallado',
					'type': 'success',
					'sticky': True,
					'message': 'Descargar Reporte De Saldos Detallado',
					'next': {'type': 'ir.actions.act_window_close'},
					'buttons':[{
						'label':'Descargar',
						'model':'ir.attachment',
						'method':'get_download_ls',
						'id':attach_id.id,
						}
					],
				}
			}


		else:
			self.env.cr.execute("""select sum(quant.quantity) as cantidad, product.default_code as default_code, product.name as nombre_producto,
					sum(prop.value_float) as precio_unitario, spl.name as lote, sl.name as ubicacion, product.id as producto_id
					from stock_quant quant
					left join product_product product on product.id = stock_quant.product_id
					left join ir_property prop on prop.res_id = 'product.product,' || product.id
					left join stock_production_lot spl on spl.id = quant.lot_id
					left join stock_location sl on sl.id = quant.location_id
					where sl.usage = 'internal' and quant.company_id = """+str(self.env.company.id)+"""
					group by product.id,
					; """)
			cnslta = self.env.cr.dictfetchall()
			tipo_cambio = self.env['res.currency.rate'].sudo().search([('name','=',(datetime.datetime.now()-timedelta(hours=5)).date()),('currency_id.name','=','USD')], limit=1)
			if len(tipo_cambio)>0:
				tasa_cambio = tipo_cambio[0].sale_type
			for x in cnslta:
				#los totales si se hacen desde la consulta son muchas variables q no funcionaran como prod con costo 0 o servicio almacenable
				total_soles += x['cantidad'] * x['precio_unitario']
			total_dolares = (total_soles/tasa_cambio) if tasa_cambio != 0 else 0
			for i in total_quants:
				worksheet.write(columna,0, str(contador),cell_n)
				worksheet.write(columna,1, str(x['default_code'] if x['default_code'] else ''),cell_n)
				worksheet.write(columna,2, str(x['nombre_producto'] if x['nombre_producto'] else ''),cell_n)
				worksheet.write(columna,3, x['cantidad'] * x['precio_unitario'],cell_numero)
				
				worksheet.write(columna,4, (((x['cantidad'] * x['precio_unitario'])*100)/total_soles) if total_soles!=0 else 0  ,cell_porcentaje)
				if tasa_cambio != 0:
					worksheet.write(columna,5, (x['cantidaad'] * x['precio_unitario'])/tasa_cambio,cell_numero_dolar)
					worksheet.write(columna,8, x['precio_unitario']/tasa_cambio,cell_numero_dolar)
					worksheet.write(columna,6, ((((x['cantidad'] * x['precio_unitario'])/tasa_cambio)*100)/total_dolares) if total_dolares != 0 else 0,cell_porcentaje)
				else:
					worksheet.write(columna,5, 0,cell_numero_dolar)
					worksheet.write(columna,6, 0,cell_porcentaje)
					worksheet.write(columna,8, 0,cell_numero_dolar)
				
				worksheet.write(columna,7, x['precio_unitario'] if x['precio_unitario'] else 0,cell_numero)

				worksheet.write(columna,9, x['cantidad'] if x['cantidad'] else 0,cell_right_n)
				worksheet.write(columna,10, str(x['lote'] if x['lote'] else ''),cell_n)
				worksheet.write(columna,11, str(x['ubicacion'] if x['ubicacion'] else ''),cell_n)
				contador = contador+1
				columna = columna+1
				
			worksheet.write(columna,2, "Total S/",cell_right)
			worksheet.write(columna,3, total_soles,cell_right_soles)
			worksheet.write(columna,4, "Total $",cell_right)
			worksheet.write(columna,5, total_dolares,cell_right_dolares)
			workbook.close()
			output.seek(0)

			attach_id = self.env['ir.attachment'].create({
						'name': "Reporte De Saldos.xlsx",
						'type': 'binary',
						'datas': base64.encodestring(output.read()),
						'eliminar_automatico': True
					})
			output.close()


			return {
				'type': 'ir.actions.client',
				'tag': 'notification_llikha',
				'params': {
					'title':'Reporte De Saldos',
					'type': 'success',
					'sticky': True,
					'message': 'Descargar Reporte De Saldos',
					'next': {'type': 'ir.actions.act_window_close'},
					'buttons':[{
						'label':'Descargar',
						'model':'ir.attachment',
						'method':'get_download_ls',
						'id':attach_id.id,
						}
					],
				}
			}
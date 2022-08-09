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
		cell_right_soles.set_num_format('##0.00')
		cell_right_soles.set_num_format('S/ #,##0;S/ -#,##0')



		cell_right_dolares = workbook.add_format({'bold': True})
		cell_right_dolares.set_align('right')
		cell_right_dolares.set_border(1)
		cell_right_dolares.set_font_name('Calibri')
		cell_right_dolares.set_font_size(11)
		cell_right_dolares.set_num_format('$ #,##0;$ -#,##0')


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
		cell_numero.set_num_format('S/ #,##0;S/ -#,##0')
		
		cell_porcentaje = workbook.add_format({'bold': False})
		cell_porcentaje.set_align('right')
		cell_porcentaje.set_border(1)
		cell_porcentaje.set_font_name('Calibri')
		cell_porcentaje.set_font_size(11)
		cell_porcentaje.set_num_format('"%" #,##0.00')

		cell_numero_dolar = workbook.add_format({'bold': False})
		cell_numero_dolar.set_align('right')
		cell_numero_dolar.set_border(1)
		cell_numero_dolar.set_font_name('Calibri')
		cell_numero_dolar.set_font_size(11)
		cell_numero_dolar.set_num_format('$ #,##0;$ -#,##0')

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
		total_quants = self.env['stock.quant'].sudo().search([('location_id.usage','=','internal'),('company_id','=',self.env.company.id)])
		tasa_cambio = 0
		tipo_cambio = self.env['res.currency.rate'].sudo().search([('name','=',(datetime.datetime.now()-timedelta(hours=5)).date()),('currency_id.name','=','USD')], limit=1)
		if len(tipo_cambio)>0:
			for l in tipo_cambio:
				tasa_cambio = l.sale_type
		for i in total_quants:
			worksheet.write(columna,0, str(contador),cell_n)
			worksheet.write(columna,1, str(i.product_id.default_code if i.product_id.default_code else ''),cell_n)
			worksheet.write(columna,2, str(i.product_id.name if i.product_id.name else ''),cell_n)
			worksheet.write(columna,3, i.quantity * i.product_id.standard_price,cell_numero)
			total_soles += i.quantity * i.product_id.standard_price
			worksheet.write(columna,4, str( ''),cell_porcentaje)
			if tasa_cambio != 0:
				total_dolares += (i.quantity * i.product_id.standard_price)/tasa_cambio
				worksheet.write(columna,5, (i.quantity * i.product_id.standard_price)/tasa_cambio,cell_numero_dolar)
				worksheet.write(columna,8, i.product_id.standard_price/tasa_cambio,cell_numero_dolar)
			else:
				worksheet.write(columna,5, 0,cell_numero_dolar)
				worksheet.write(columna,8, 0,cell_numero_dolar)
			worksheet.write(columna,6, str(''),cell_porcentaje)
			worksheet.write(columna,7, i.product_id.standard_price if i.product_id.standard_price else 0,cell_numero)

			worksheet.write(columna,9, i.quantity if i.quantity else 0,cell_right_n)
			worksheet.write(columna,10, str(i.lot_id.name if i.lot_id.name else ''),cell_n)
			worksheet.write(columna,11, str(i.location_id.name if i.location_id.name else ''),cell_n)
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
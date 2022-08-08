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
		worksheet = workbook.add_worksheet("SALDO VALORES DE CIERRE")
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
		worksheet.set_column('K:K', 25)
		
		cell_titulo = workbook.add_format({'bold': True})
		cell_titulo.set_align('center')
		cell_titulo.set_border(2)
		cell_titulo.set_font_name('Calibri')
		cell_titulo.set_font_size(15)

		cell_r = workbook.add_format({'bold': True})
		cell_r.set_align('center')
		cell_r.set_border(2)
		cell_r.set_font_name('Calibri')
		cell_r.set_font_size(12)		



		cell_n = workbook.add_format({'bold': False})
		cell_n.set_align('center')
		cell_n.set_border(1)
		cell_n.set_font_name('Calibri')
		cell_n.set_font_size(11)

		cell_numero = workbook.add_format({'bold': False})
		cell_numero.set_align('center')
		cell_numero.set_border(1)
		cell_numero.set_font_name('Calibri')
		cell_numero.set_font_size(11)
		cell_numero.set_num_format('0.000')

		import datetime
		from datetime import timedelta
		worksheet.merge_range(1,2,2,10, "VALORES AL CIERRE"+str((datetime.datetime.now()-timedelta(hours=5)).date()), cell_titulo)

		worksheet.set_row(4, 28.20)
		worksheet.set_row(5, 28.20)

		worksheet.merge_range('A5:C6', "ARTICULO", cell_r)
		worksheet.merge_range('D5:D6', "SALDO S/.", cell_r)
		worksheet.merge_range('E5:E6', "% SOLES", cell_r)
		worksheet.merge_range('F5:F6', "SALDO US $", cell_r)
		worksheet.merge_range('G5:G6', "% DOLARES", cell_r)
		worksheet.merge_range('H5:H6', "VALOR UNIT S/.", cell_r)
		worksheet.merge_range('I5:I6', "VALOR UNIT $", cell_r)
		worksheet.merge_range('J5:J6', "SALDO CANTIDAD", cell_r)
		worksheet.merge_range('K5:K6', "MOVIMIENTO CONTRA CANTIDAD", cell_r)
		columna = 6
		contador = 1
		import datetime
		from datetime import timedelta
		total_quants = self.env['stock.quant'].sudo().search([])
		tasa_cambio = 0
		tipo_cambio = self.env['res.currency.rate'].sudo().search([('name','=',(datetime.datetime.now()-timedelta(hours=5)).date()),('currency_id.name','=','USD')], limit=1)
		if len(tipo_cambio)>0:
			for l in tipo_cambio:
				tasa_cambio = l.sale_type
		for i in total_quants:
			worksheet.write(columna,0, str(contador),cell_n)
			worksheet.write(columna,1, str(i.product_id.default_code if i.product_id.default_code else ''),cell_n)
			worksheet.write(columna,2, str(i.product_id.name if i.product_id.name else ''),cell_n)
			worksheet.write(columna,3, str(i.quantity * i.product_id.standard_price),cell_numero)
			worksheet.write(columna,4, str( ''),cell_n)
			if tasa_cambio != 0:
				worksheet.write(columna,5, str( (i.quantity * i.product_id.standard_price)/tasa_cambio),cell_numero)
				worksheet.write(columna,8, str(i.product_id.standard_price/tasa_cambio),cell_numero)
			else:
				worksheet.write(columna,5, str(0),cell_numero)
				worksheet.write(columna,8, str(0),cell_numero)
			worksheet.write(columna,6, str(''),cell_n)
			worksheet.write(columna,7, str(i.product_id.standard_price if i.product_id.standard_price else 0),cell_numero)

			worksheet.write(columna,9, str(i.quantity if i.quantity else 0),cell_numero)
			worksheet.write(columna,10, '',cell_n)
			contador = contador+1
			columna = columna+1
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
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

class mrp_production(models.Model):
	_inherit = "mrp.production"

	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()

		#direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(output, {'constant_memory': True})
		worksheet = workbook.add_worksheet("FORMATO DE ORDEN DE PRODUCCIÓN")
		x= 9

		worksheet.set_column('A:A', 12.80)
		worksheet.set_column('B:B', 12.80)
		worksheet.set_column('C:C', 12.80)
		worksheet.set_column('D:D', 12.80)
		worksheet.set_column('E:E', 12.80)
		worksheet.set_column('F:F', 12.80)
		worksheet.set_column('G:G', 12.80)
		worksheet.set_column('H:H', 12.80)
		worksheet.set_column('I:I', 12.80)
		worksheet.set_column('J:J', 12.80)
		worksheet.set_column('K:K', 12.80)
		worksheet.set_column('L:L', 12.80)
		worksheet.set_column('M:M', 12.80)
		worksheet.set_column('N:N', 12.80)
		worksheet.set_column('O:O', 12.80)
		worksheet.set_column('P:P', 12.80)
		worksheet.set_column('Q:Q', 12.80)
		worksheet.set_column('R:R', 12.80)
		worksheet.set_column('S:S', 12.80)
		worksheet.set_column('T:Z', 12.80)

		boldbord = workbook.add_format({'bold': True})
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_name('Calibri')
		boldbord.set_font_size(11)


		cell_titulo = workbook.add_format({'bold': True})
		cell_titulo.set_align('center')
		cell_titulo.set_border(5)
		cell_titulo.set_font_name('Calibri')
		cell_titulo.set_font_size(12)
		cell_titulo.set_bg_color('#D1DFF5')





		cell = workbook.add_format({'bold': True})
		cell.set_align('center')
		cell.set_border(4)
		cell.set_font_name('Calibri')
		cell.set_font_size(12)
		cell.set_bg_color('#DBE6F5')

		cell_r = workbook.add_format({'bold': True})
		cell_r.set_align('center')
		cell_r.set_border(4)
		cell_r.set_font_name('Calibri')
		cell_r.set_font_size(12)		
		cell_r.set_bg_color('#F7E7F3')
		
		cell_n = workbook.add_format({'bold': False})
		cell_n.set_align('center')
		cell_n.set_border(4)
		cell_n.set_font_name('Calibri')
		cell_n.set_font_size(11)

		worksheet.merge_range(0,2,1,10, "FORMATO DE ORDEN DE PRODUCCIÓN - STOCK", cell_titulo)


		worksheet.write(3,0, "CONCEPTO",boldbord)
		worksheet.write(3,8, "N. ORDEN DE PRODUCCIÓN :",boldbord)
		worksheet.write(3,9, "___________________",boldbord)
		worksheet.write(4,0, "Camb. Codigo",boldbord)
		worksheet.write(5,0, "Mezcla",boldbord)
		worksheet.write(6,0, "Reenvase",boldbord)
		worksheet.write(7,0, "Dilucion",boldbord)
		worksheet.write(4,3, "FECHA SOL:",boldbord)
		worksheet.write(4,4, str(self.date_planned_start if self.date_planned_start else ''),boldbord)
		worksheet.write(5,3, "FECHA PROD:",boldbord)
		worksheet.write(5,4, str(self.date_planned_start if self.date_planned_start else ''),boldbord)

		worksheet.merge_range(9,0,9,12, "PRODUCTO FINAL", cell_r)
		worksheet.write(10,0, "Codigo",cell)
		worksheet.merge_range(10,1,10,6, "DESCRIPCIÓN", cell)
		worksheet.write(10,7, "CANT",cell)
		worksheet.write(10,8, "UND",cell)
		worksheet.merge_range(10,9,10,12, "OBSERVACIÓN", cell)



		worksheet.write(11,0, str(self.product_id.default_code if self.product_id.default_code else ''),cell_n)
		worksheet.merge_range(11,1,12,6, str(self.product_id.name if self.product_id.name else ''), cell_n)
		worksheet.write(11,7, str(self.product_qty if self.product_qty else 0),cell_n)
		worksheet.write(11,8, str(self.product_uom_id.name if self.product_uom_id.name else ''),cell_n)
		worksheet.merge_range(11,9,11,12, "", cell_n)
			
			
		worksheet.merge_range(12,0,12,12, "MATERIA PRIMA", cell_r)
		worksheet.write(13,0, "Codigo",cell)
		worksheet.merge_range(13,1,14,6, "DESCRIPCIÓN", cell)
		worksheet.write(13,7, "CANT",cell)
		worksheet.write(13,8, "UND",cell)
		worksheet.merge_range(13,9,13,12, "OBSERVACIÓN", cell)
		columna = 14
		for lineas in self.move_raw_ids:
			worksheet.write(columna,0, str(lineas.product_id.default_code if lineas.product_id.default_code else ''),cell_n)
			worksheet.merge_range(columna,1,columna,6, str(lineas.product_id.name if lineas.product_id.name else ''), cell_n)
			worksheet.write(columna,7, str(lineas.quantity_done if lineas.quantity_done else 0),cell_n)
			worksheet.write(columna,8, str(lineas.product_uom.name if lineas.product_uom.name else ''),cell_n)
			worksheet.merge_range(columna,9,columna,12, "", cell_n)
			columna = columna+1



		#def action_see_move_scrap(self):
		#self.ensure_one()
		#action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
		#action['domain'] = [('production_id', '=', self.id)]
		#action['context'] = dict(self._context, default_origin=self.name)
		#return action

		worksheet.merge_range(columna,0,columna,12, "MERMA", cell_r)
		columna = columna+1
		worksheet.write(columna,0, "Codigo",cell)
		worksheet.merge_range(columna,1,columna,6, "DESCRIPCIÓN", cell)
		worksheet.write(columna,7, "CANT",cell)
		worksheet.write(columna,8, "UND",cell)
		worksheet.merge_range(columna,9,columna,12, "OBSERVACIÓN", cell)
		columna = columna+1
		scrapss = self.env['stock.scrap'].sudo().search([
			('production_id', '=', self.id)
			])
		if len(scrapss)>0:
			for li_scra in scrapss:
				worksheet.write(columna,0, str(li_scra.product_id.default_code if li_scra.product_id.default_code else ''),cell)
				worksheet.merge_range(columna,1,columna,6, str(li_scra.product_id.name if li_scra.product_id.name else ''), cell)
				worksheet.write(columna,7, str(li_scra.scrap_qty if li_scra.scrap_qty else 0),cell)
				worksheet.write(columna,8, str(li_scra.product_uom_id.name if li_scra.product_uom_id.name else ''),cell)
				worksheet.merge_range(columna,9,columna,12, "", cell)
				columna = columna+1


		worksheet.merge_range(columna,0,columna,12, "DESMEDRO", cell_r)
		columna = columna+1
		worksheet.write(columna,0, "Codigo",cell)
		worksheet.merge_range(columna,1,columna,6, "DESCRIPCIÓN", cell)
		worksheet.write(columna,7, "CANT",cell)
		worksheet.write(columna,8, "UND",cell)
		worksheet.merge_range(columna,9,columna,12, "OBSERVACIÓN", cell)
		columna = columna+1
		for sub_prod in self.move_byproduct_ids:
			worksheet.write(columna,0, str(sub_prod.product_id.default_code if sub_prod.product_id.default_code else ''),cell_n)
			worksheet.merge_range(columna,1,columna,6, str(sub_prod.product_id.name if sub_prod.product_id.name else ''), cell_n)
			worksheet.write(columna,7, str(lineas.product_uom_qty if lineas.product_uom_qty else 0),cell_n)
			worksheet.write(columna,8, str(lineas.product_uom.name if lineas.product_uom.name else ''),cell_n)
			worksheet.merge_range(columna,9,columna,12, "", cell_n)
			columna = columna+1

		import datetime		


		import datetime

		workbook.close()
		output.seek(0)

		attach_id = self.env['ir.attachment'].create({
					'name': "prueba.xlsx",
					'type': 'binary',
					'datas': base64.encodestring(output.read()),
					'eliminar_automatico': True
				})
		output.close()


		return {
			'type': 'ir.actions.client',
			'tag': 'notification_llikha',
			'params': {
				'title':'prueba',
				'type': 'success',
				'sticky': True,
				'message': 'Se proceso',
				'next': {'type': 'ir.actions.act_window_close'},
				'buttons':[{
					'label':'Descargar prueba',
					'model':'ir.attachment',
					'method':'get_download_ls',
					'id':attach_id.id,
					}
				],
			}
		}

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
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_name('Calibri')
		boldbord.set_font_size(11)



		cell = WriteOnlyCell(worksheet, value="FORMATO DE ORDEN DE PRODUCCIÓN - STOCK")
		cell.font = Font(name='Calibri',size=18,bold=True)
		cell.set_bg_color('#DCE6F1')
		cell.alignment = Alignment(horizontal='center')
		
		worksheet.merged_cells.ranges.append(get_column_letter(4)+ "1:" + get_column_letter(11) + '1')
		worksheet.append(["","","","","","",cell])

		worksheet.append([""])
		worksheet.write(1,4, "CONCEPTO",boldbord)
		worksheet.write(1,5, "Camb. Codigo",boldbord)
		worksheet.write(1,6, "Mezcla",boldbord)
		worksheet.write(1,7, "Reenvase",boldbord)
		worksheet.write(1,8, "Dilucion",boldbord)
		worksheet.write(4,5, "FECHA SOL:",boldbord)
		worksheet.write(5,5, str(self.date_planned_start),boldbord)
		worksheet.write(4,6, "FECHA PROD:",boldbord)
		worksheet.write(5,6, str(self.date_planned_start),boldbord)
		
		
			
		import datetime		


		import datetime

		workbook.save(output)
		output.seek(0)

		attach_id = self.env['ir.attachment'].create({
					'name': "FORMATO DE ORDEN DE PRODUCCIÓN.xlsx",
					'type': 'binary',
					'datas': base64.encodestring(output.read()),
					'eliminar_automatico': True
				})
		output.close()


		return {
			'notif_button':{'auto_close':False,'with_menssage':1,'title':'FORMATO DE ORDEN DE PRODUCCIÓN','message':'Se proceso ','eventID':attach_id.id,'model_notify':'ir.attachment','method_notify':'get_download_ls','name_button':'Descargar FORMATO DE ORDEN DE PRODUCCIÓN'}
		}
	

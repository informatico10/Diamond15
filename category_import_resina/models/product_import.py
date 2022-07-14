from openerp import models, fields, exceptions, api, _
import tempfile
import binascii
import xlrd
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import UserError
from openerp.exceptions import Warning, UserError
import io
import logging
_logger = logging.getLogger(__name__)

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')


class product_category_import(models.TransientModel):
	_name = "product.category.import.resin"
	_description = "Importador Categorias Producto"

	file = fields.Binary(string='Archivo')	
	import_tarifa_type = fields.Selection([('create','Crear Tarifas'),('update','Actualizar Tarifas')],string='Tipo de Operacion', required=True,default="create")
	
	def verify_if_exists_product(self):
		fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
		try :
			fp.write(binascii.a2b_base64(self.file))
			fp.seek(0)
			values = {}
			res = {}
			result = []
			workbook = xlrd.open_workbook(fp.name)
		except Exception:
				raise UserError(_("Sube un archivo .xlsx!")) 
		sheet = workbook.sheet_by_index(0)
		for row_no in range(sheet.nrows):
			val = {}
			if row_no <= 0:
				fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
			else:
				line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
				values.update( {'default_code': line[0],
							})
				gg = self.verify_product(values)
				if gg:
					result.append(gg)

		if len(result)>0:
			import io
			from xlsxwriter.workbook import Workbook
			ReportBase = self.env['report.base']

			direccion = self.env['main.parameter'].search([('company_id','=',self.env.company.id)],limit=1).dir_create_file

			if not direccion:
				raise UserError(u'No existe un Directorio Exportadores configurado en Parametros Principales de Contabilidad para su Compañía')

			workbook = Workbook(direccion +'Productos_Existentes.xlsx')
			workbook, formats = ReportBase.get_formats(workbook)

			import importlib
			import sys
			importlib.reload(sys)

			worksheet = workbook.add_worksheet("Productos")
			worksheet.set_tab_color('blue')

			HEADERS = ['REFERENCIA INTERNA']
			worksheet = ReportBase.get_headers(worksheet,HEADERS,0,0,formats['boldbord'])
			x=1

			for line in result:
				worksheet.write(x,0,line[0] if line[0] else '',formats['especial1'])				
				x += 1

			widths = [100,19]
			worksheet = ReportBase.resize_cells(worksheet,widths)
			workbook.close()

			f = open(direccion +'Productos_Existentes.xlsx', 'rb')
			raise UserError("Productos Duplicados")
			return self.env['popup.it'].get_file('Productos Duplicados.xlsx',base64.encodestring(b''.join(f.readlines())))
		else:
			pass
			#return self.env['popup.it'].get_message('NO EXISTEN PRODUCTOS DUPLICADOS.')

	def verify_product(self, values):
		s = str(values.get('default_code')).strip()
		default_code = s.rstrip('0').rstrip('.') if '.' in s else s
		product_id = False		
		product_id = self.env['product.template'].search([('default_code','=', default_code)],limit=1)
		
		if product_id:
			return [default_code]

	def tarifa_import(self):              
		fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
		try :
			fp.write(binascii.a2b_base64(self.file))
			fp.seek(0)
			values = {}
			res = {}
			workbook = xlrd.open_workbook(fp.name)
		except Exception:
				raise UserError(_("Sube un archivo .xlsx!")) 
		sheet = workbook.sheet_by_index(0)
		for row_no in range(sheet.nrows):
			val = {}
			if row_no <= 0:
				fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
			else:
				line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
				if self.import_tarifa_type == 'create':
					values.update( {'name':line[0],
								'parent_id': line[1],
								'metodo_coste': line[2],
								'cuenta_ingreso': line[3],
								'cuenta_gasto': line[4],
								})
					res = self.product_create(values)
				else:					
					if line[0]=='':
						raise UserError('Campo NOMBRE CATEGORIA no puede estar vacío')
					if line[2]=='':
						raise UserError('Campo METODO DE COSTE no puede estar vacío')
					if line[3]=='':
						raise UserError('Campo CUENTA DE INGRESO no puede estar vacío')	  
					if line[4]=='':
						raise UserError('Campo CUENTA DE GASTO no puede estar vacío')
										
					categoria = False
					if line[1].strip()!='':
						product_categ_obj = self.env['product.category']
						padre_id = False
						for i in line[1].split('|'):
							categ_id = product_categ_obj.search([('name','=',str(i).strip()),('parent_id','=',padre_id)])
							categoria = categ_id
							padre_id = categ_id.id
							if categ_id.id == False:
								raise UserError('Categoria no encontrado: ' + str(i))
					type = False
					if line[2]=='standard':
						type = 'standard'
					elif line[2]=='fifo':
						type = 'fifo'
					elif line[2]=='promedio':
						type = 'average'
					else:
						raise UserError('Método de Coste No Encontrado: ' + str(line[2]))

					final_ingreso = line[3].strip()
					if final_ingreso[0] == "'":
						final_ingreso = final_ingreso[1:]
					if final_ingreso[-1] == "'":
						final_ingreso = final_ingreso[:1]
					cuenta_de_ingreso = self.env['account.account'].sudo().search([('code', '=', final_ingreso), '|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])
					if cuenta_de_ingreso:
						if len(cuenta_de_ingreso)>1:
							raise UserError("Dos Cuentas De Ingreso Con El Mismo Codigo: " + str(line[3]))							
						else:
							final_gasto = line[4].strip()
							if final_gasto[0] == "'":
								final_gasto = final_gasto[1:]
							if final_gasto[-1] == "'":
								final_gasto = final_gasto[:1]
							cuenta_de_gasto = self.env['account.account'].sudo().search([('code', '=', final_gasto), '|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])
							if cuenta_de_gasto:
								if len(cuenta_de_gasto)>1:
									raise UserError("Dos Cuentas De Gasto Con El Mismo Codigo: " + str(line[4]))
								else:
									categoria_actual = self.env['product.category'].sudo().search([('name', '=', line[0].strip()), ('parent_id', '=', categoria.id if categoria!=False else False)])
									if categoria_actual:
										if len(categoria_actual)>1:
											raise UserError('Se Encontraron Mas De Una Categoria A Actualizar, Nombre: ' + str(line[0]) + " Con La Categoria Padre: " + str(categoria.name if categoria != False else ""))
										else:
											categoria_actual.sudo().write({'property_cost_method':type, 'property_account_income_categ_id':cuenta_de_ingreso.id, 'property_account_expense_categ_id':cuenta_de_gasto.id})
									else:
										raise UserError('Categoria A Actualizar No Encontrada, Nombre: ' + str(line[0]) + " Con La Categoria Padre: " + str(categoria.name if categoria != False else ""))
							else:
								raise UserError('Cuenta de Gasto No Encontrada: ' + str(line[4]))
					else:
						raise UserError('Cuenta De Ingreso No Encontrada: ' + str(line[3]))
		return self.env['popup.it'].get_message('SE IMPORTARON LAS CATEGORIAS DE MANERA CORRECTA.')
	
	def product_create(self, values):
		categ_obj = self.env['product.category']
		if values.get('name') == '':
			raise UserError('Campo NOMBRE CATEGORIA no puede estar vacío')			
		if values.get('metodo_coste') == '':
			raise UserError('Campo METODO DE COSTE no puede estar vacío')
		if values.get('cuenta_ingreso') == '':
			raise UserError('Campo CUENTA DE INGRESO no puede estar vacío')
		if values.get('cuenta_gasto') == '':
			raise UserError('Campo CUENTA DE GASTO no puede estar vacío')
		categoria = False
		if values.get('parent_id').strip()!='':
			padre_id = False
			product_categ_obj = self.env['product.category']
			for i in values.get('parent_id').split('|'):
				categ_id = product_categ_obj.search([('name','=',str(i).strip()),('parent_id','=',padre_id)])
				categoria = categ_id
				padre_id = categ_id.id
				if categ_id.id == False:
					raise UserError('Categoria no encontrado: ' + str(i))

		type = False
		if values.get('metodo_coste')=='standard':
			type = 'standard'
		elif values.get('metodo_coste')=='fifo':
			type = 'fifo'
		elif values.get('metodo_coste')=='promedio':
			type = 'average'
		else:
			raise UserError('Método de Coste No Encontrado: ' + str(values.get('metodo_coste')))


		final_ingreso = values.get('cuenta_ingreso').strip()
		if final_ingreso[0] == "'":
			final_ingreso = final_ingreso[1:]
		if final_ingreso[-1] == "'":
			final_ingreso = final_ingreso[:1]
		cuenta_de_ingreso = self.env['account.account'].sudo().search([('code', '=', final_ingreso), '|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])
		if cuenta_de_ingreso:
			if len(cuenta_de_ingreso)>1:
				raise UserError("Dos Cuentas De Ingreso Con El Mismo Codigo: " + str(values.get('cuenta_ingreso')))
			else:
				final_gasto = values.get('cuenta_gasto').strip()
				if final_gasto[0] == "'":
					final_gasto = final_gasto[1:]
				if final_gasto[-1] == "'":
					final_gasto = final_gasto[:1]
				cuenta_de_gasto = self.env['account.account'].sudo().search([('code', '=', final_gasto), '|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])
				if cuenta_de_gasto:
					if len(cuenta_de_gasto)>1:
						raise UserError("Dos Cuentas De Gasto Con El Mismo Codigo: " + str(values.get('cuenta_gasto')))					
				else:
					raise UserError('Cuenta de Gasto No Encontrada: ' + str(values.get('cuenta_gasto')))
		else:
			raise UserError('Cuenta De Ingreso No Encontrada: ' + str(values.get('cuenta_ingreso')))


		categoria_actual_repetida = self.env['product.category'].sudo().search([('name', '=', values.get('name').strip()), ('parent_id', '=', categoria.id if categoria!=False else False)])
		if categoria_actual_repetida:
			return
			
		vals = {
      				'name': values.get('name'),
					'parent_id': categoria.id if categoria!=False else False,
					'property_cost_method': type,
					'property_account_income_categ_id': cuenta_de_ingreso.id,
					'property_account_expense_categ_id': cuenta_de_gasto.id
								  }
		
		res = categ_obj.create(vals)
		return res	

	def download_template(self):
		return {
			 'type' : 'ir.actions.act_url',
			 'url': '/web/binary/download_category_import_template',
			 'target': 'new',
			}

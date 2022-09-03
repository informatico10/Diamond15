# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import base64

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4,letter
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import simpleSplit
import decimal

class AccountMove(models.Model):
	_inherit = 'landed.cost.it'

	adua_agent = fields.Many2one('res.partner',string='Agente de Aduana',copy=False)
	
	def get_pdf_libro_caja(self):
		import importlib
		import sys
		importlib.reload(sys)

		def _get_sql_vst_caja(self):
			sql = """
				SELECT 
				gc.cuenta,
				aa.name as name_cuenta,
				gc.voucher,
				to_char(gc.fecha::timestamp with time zone, 'yyyy/mm/dd'::text) as fecha,
				gc.glosa,
				gc.debe,
				gc.haber
				FROM get_caja_bancos('%s','%s',%s) gc
				LEFT JOIN account_account aa ON aa.id = gc.account_id
				WHERE LEFT(gc.cuenta,3) = '101'
			
			""" % (self.period.date_start.strftime('%Y/%m/%d'),
				self.period.date_end.strftime('%Y/%m/%d'),
				str(self.company_id.id))

			return sql

		def particionar_text(c,tam):
			tet = ""
			for i in range(len(c)):
				tet += c[i]
				lines = simpleSplit(tet,'Helvetica',8,tam)
				if len(lines)>1:
					return tet[:-1]
			return tet

		def pdf_header(self,c,wReal,hReal,size_widths,product):
			c.setFont("Helvetica-Bold", 11)
			c.setFillColor(colors.black)
			c.drawCentredString((wReal/2)+20,hReal, u"LIQUIDACIÓN DE IMPORTACIÓN : %s "%(self.name))
			c.setFont("Helvetica-Bold", 8)
			c.drawString(30,hReal-12, particionar_text( self.company_id.name,120))
			#c.drawString(30,hReal-22,particionar_text( self.company_id.partner_id.street if self.company_id.partner_id.street else '',100))
			#c.drawString(30,hReal-32, self.company_id.partner_id.state_id.name if self.company_id.partner_id.state_id else '')
			#c.drawString(30,hReal-42, self.company_id.partner_id.vat if self.company_id.partner_id.vat else '')


			c.setFont("Helvetica-Bold", 9)
			style = getSampleStyleSheet()["Normal"]
			style.leading = 8
			style.alignment= 1

			c.drawString(30,hReal-55,'Producto:')
			c.drawString(30,hReal-66, 'Proveedor:')
			c.drawString(30,hReal-77, 'Orden de Compra:')
			c.drawString(30,hReal-88, 'Proyecto:')
			c.drawString(30,hReal-99, 'Tipo Transporte:')
			c.drawString(30,hReal-110, 'Agente de aduana:')
			c.drawString(30,hReal-121, 'DUA:')

			c.drawString(150,hReal-55,'Fecha de Orden:')
			c.drawString(150,hReal-66, 'Fecha de Llegada:')
			c.drawString(150,hReal-77, 'Origen:')
			c.drawString(150,hReal-88, 'Proyecto:')
			c.drawString(150,hReal-99, 'INCOTERMS:')
			c.drawString(150,hReal-110, 'Cantidad:')
			c.drawString(150,hReal-121, 'Factor Imp Ext:')

			data= [[Paragraph("<font size=8><b>Concepto/Documento</b></font>",style), 
				Paragraph("<font size=8><b>Num Docum</b></font>",style), 
				Paragraph("<font size=8><b>Mon</b></font>",style), 
				Paragraph("<font size=8><b>T/C</b></font>",style),
				Paragraph("<font size=8><b>Valor Compra</b></font>",style),
				Paragraph("<font size=8><b>Costo Ext</b></font>",style),
				Paragraph("<font size=8><b>Costo Nac</b></font>",style)]]
			t=Table(data,colWidths=size_widths, rowHeights=(20))
			t.setStyle(TableStyle([
				('SPAN',(0,0),(0,1)),
				('SPAN',(1,0),(1,1)),
				('SPAN',(2,0),(2,1)),
				('SPAN',(3,0),(4,0)),
				('GRID',(0,0),(-1,-1), 1, colors.black),
				('ALIGN',(0,0),(-1,-1),'LEFT'),
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('TEXTFONT', (0, 0), (-1, -1), 'Calibri'),
				('FONTSIZE',(0,0),(-1,-1),4)
			]))
			t.wrapOn(c,30,500) 
			t.drawOn(c,30,hReal-180)

		def verify_linea(self,c,wReal,hReal,posactual,valor,pagina,size_widths):
			if posactual <50:
				c.showPage()
				pdf_header(self,c,wReal,hReal,size_widths)
				return pagina+1,hReal-95
			else:
				return pagina,posactual-valor

		width ,height  = A4  # 595 , 842
		wReal = width- 15
		hReal = height - 40

		direccion = self.env['account.main.parameter'].search([('company_id','=',self.company_id.id)],limit=1).dir_create_file
		name_file = "libro_caja.pdf"
		c = canvas.Canvas( direccion + name_file, pagesize= A4 )
		pos_inicial = hReal-50
		pagina = 1

		size_widths = [175,80,20,40,80,70,70]

		pdf_header(self,c,wReal,hReal,size_widths)

		pos_inicial = pos_inicial-55

		c.setFont("Helvetica", 8)
		pagina, pos_inicial = verify_linea(self,c,wReal,hReal,pos_inicial,12,pagina,size_widths)

		self.env.cr.execute(_get_sql_vst_caja(self))
		res = self.env.cr.dictfetchall()

		cont = 0
		cuenta = ''
		sum_debe = 0
		sum_haber = 0
		saldo_debe = 0
		saldo_haber = 0

		for i in res:
			first_pos = 30
			
			c.setFont("Helvetica-Bold", 10)
			if cont == 0:
				cuenta = i['cuenta']
				cont += 1
				c.drawString( first_pos+2 ,pos_inicial,'Cuenta: ' + cuenta + ' ' + i['name_cuenta'])
				pos_inicial -= 15

			if cuenta != i['cuenta']:
				c.setFont("Helvetica-Bold", 9)
				c.line(425,pos_inicial+3,565,pos_inicial+3)
				c.drawString( 350 ,pos_inicial-10,'TOTALES:')
				c.drawRightString( 495,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % sum_debe)) )
				c.drawRightString( 565 ,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % sum_haber)))
				pos_inicial -= 10

				pagina, pos_inicial = verify_linea(self,c,wReal,hReal,pos_inicial,12,pagina,size_widths)
				c.setFont("Helvetica-Bold", 9)

				c.line(425,pos_inicial+3,565,pos_inicial+3)
				c.drawString( 350 ,pos_inicial-10,'SALDO FINAL:')
				saldo_debe = (sum_debe - sum_haber) if sum_debe > sum_haber else 0
				saldo_haber = 0 if sum_debe > sum_haber else (sum_haber - sum_debe)

				c.drawRightString( 495,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % saldo_debe)) )
				c.drawRightString( 565 ,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % saldo_haber)))
				pos_inicial -= 20

				c.line(425,pos_inicial+3,565,pos_inicial+3)

				sum_debe = 0
				sum_haber = 0

				pagina, pos_inicial = verify_linea(self,c,wReal,hReal,pos_inicial,12,pagina,size_widths)
				c.setFont("Helvetica-Bold", 10)

				cuenta = i['cuenta']
				c.drawString( first_pos+2 ,pos_inicial,'Cuenta: ' + cuenta + ' ' + i['name_cuenta'])
				pos_inicial -= 15


			c.setFont("Helvetica", 8)
			c.drawString( first_pos+2 ,pos_inicial,particionar_text( i['voucher'] if i['voucher'] else '',50) )
			first_pos += size_widths[0]

			c.drawString( first_pos+2 ,pos_inicial,particionar_text( i['fecha'] if i['fecha'] else '',50) )
			first_pos += size_widths[1]

			c.drawString( first_pos+2 ,pos_inicial,particionar_text( i['glosa'] if i['glosa'] else '',150) )
			first_pos += size_widths[2]

			c.drawRightString( first_pos+70 ,pos_inicial,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % i['debe'])) )
			sum_debe += i['debe']
			first_pos += size_widths[3]

			c.drawRightString( first_pos+70 ,pos_inicial,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % i['haber'])))
			sum_haber += i['haber']

			pagina, pos_inicial = verify_linea(self,c,wReal,hReal,pos_inicial,12,pagina,size_widths)

		c.setFont("Helvetica-Bold", 9)
		c.line(425,pos_inicial+3,565,pos_inicial+3)
		c.drawString( 350 ,pos_inicial-10,'TOTALES:')
		c.drawRightString( 495,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % sum_debe)) )
		c.drawRightString( 565 ,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % sum_haber)))
		pos_inicial -= 10

		pagina, pos_inicial = verify_linea(self,c,wReal,hReal,pos_inicial,12,pagina,size_widths)
		c.setFont("Helvetica-Bold", 9)

		c.line(425,pos_inicial+3,565,pos_inicial+3)
		c.drawString( 350 ,pos_inicial-10,'SALDO FINAL:')
		saldo_debe = (sum_debe - sum_haber) if sum_debe > sum_haber else 0
		saldo_haber = 0 if sum_debe > sum_haber else (sum_haber - sum_debe)

		c.drawRightString( 495,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % saldo_debe)) )
		c.drawRightString( 565 ,pos_inicial-10,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % saldo_haber)))
		pos_inicial -= 20

		c.line(425,pos_inicial+3,565,pos_inicial+3)

		c.save()

		f = open(str(direccion) + name_file, 'rb')		
		return self.env['popup.it'].get_file('LIBRO CAJA '+ self.period.name,base64.encodestring(b''.join(f.readlines())))
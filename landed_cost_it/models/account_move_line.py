# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'
	
	invoice_date_landed = fields.Date(related='move_id.invoice_date',string='Fecha Factura')
	is_landed = fields.Boolean(related='product_id.product_tmpl_id.is_landed_cost',string='Usa GV')
# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class AccountAssetAsset(models.Model):
	_inherit = 'account.asset.asset'

	area = fields.Char(string='Area')
	encargado = fields.Char(string='Encargado')

	# @api.model
	# def create(self, vals):
	# 	id_seq = self.env['ir.sequence'].search([('name', '=', 'Activos Diamond IT'),('company_id','=',self.env.company.id)],limit=1)
	#
	# 	if not id_seq:
	# 		id_seq = self.env['ir.sequence'].create({'name': 'Activos Diamond IT',
	# 		'company_id': self.env.company.id,
	# 		'implementation': 'no_gap',
	# 		'active': True,
	# 		'prefix': '',
	# 		'padding': 4,
	# 		'number_increment': 1,
	# 		'number_next_actual': 1})
	#
	# 	code = id_seq._next()
	# 	vals['code'] = '1' + datetime.strptime(vals['date'], '%Y-%m-%d').strftime('%y%m') + code
	# 	t = super(AccountAssetAsset, self).create(vals)
	# 	return t

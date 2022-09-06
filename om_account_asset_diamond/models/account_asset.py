# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountAssetAsset(models.Model):
	_inherit = 'account.asset.asset'

	area = fields.Char(string='Area')
	encargado = fields.Char(string='Encargado')
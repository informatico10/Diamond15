# -*- coding:utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	def create_landed_cost(self):
		landed = self.env['landed.cost.it'].create({
			'date_kardex': fields.Datetime.now(),
			'company_id': self.company_id.id,
		})
		for p in self.picking_ids:
			p.landed_cost_id = landed.id

		return {
			'view_mode': 'form',
			'view_id': self.env.ref('landed_cost_it.view_landed_cost_it_form').id,
			'res_model': 'landed.cost.it',
			'type': 'ir.actions.act_window',
			'res_id': landed.id,
		}
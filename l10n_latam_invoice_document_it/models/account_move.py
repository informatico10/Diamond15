# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api

class AccountMove(models.Model):
	_inherit = "account.move"

	def _compute_l10n_latam_document_type(self):
		for rec in self.filtered(lambda x: x.state == 'draft'):
			rec.l10n_latam_document_type_id = rec.l10n_latam_document_type_id.id
# -*- coding: utf-8 -*-
import requests
import json

from odoo import fields, models, api
import logging
log = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_pe_prepare_dte(self):
        res = super(AccountMove, self)._l10n_pe_prepare_dte()
        if self.purchase_ebill:
            res["service_order"] = self.purchase_ebill
        return res

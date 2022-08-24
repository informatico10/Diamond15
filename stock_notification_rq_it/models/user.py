from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsersStockNotification(models.Model):
    _inherit = 'res.users'

    warehouse_responsable_id = fields.Many2many('stock.warehouse', string='Almacén Responsable')

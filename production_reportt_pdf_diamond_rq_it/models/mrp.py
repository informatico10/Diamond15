from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class MrpProductionReportPdf(models.Model):
    _inherit = 'mrp.production'

    concepto = fields.Selection([
        ('0', 'Camb. Código'),
        ('1', 'Mezcla'),
        ('2', 'Reenvase'),
        ('3', 'Dilución'),
    ], string='Concepto')
    observation = fields.Text('Observaciones')
    workers = fields.Html('Trabajadores')
    merma = fields.Char('Merma')
    desmedro = fields.Char('Desmedro')
    hr_start = fields.Date('H. Inicio')
    hr_end = fields.Date('H. Fin')

    suministros = fields.Selection([
        ('0', 'Cilindros'),
        ('1', 'Hoovers'),
        ('2', 'Bolsa de Papel'),
        ('3', 'Bolsas de PP'),
        ('4', 'Cisterna/tanque'),
        ('5', 'Big Bag'),
        ('6', 'Galoneras'),
    ], string='Suministros')

    team = fields.Selection([
        ('0', 'Agitador'),
        ('1', 'Bombas'),
        ('2', 'Montacargas'),
    ], string='Equipo')

    signature_aux_production = fields.Binary('Firma Aux Producción')
    signature_aux_warehouse = fields.Binary('Firma Aux Almacén')


class StockMoveReportPdf(models.Model):
    _inherit = 'stock.move'
    _description = 'Stock Move'

    observation = fields.Text('Observaciones')

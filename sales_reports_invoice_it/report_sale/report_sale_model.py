
from pyparsing import line
from odoo import models, fields, api,tools
from datetime import datetime, timedelta


class ReportSaleSelect(models.Model):
    _name = 'report.sale.select'
    _description ="Report Sale Select"
    _auto = False

    # general
    type_partner_product = fields.Selection([
        ('partner', 'Cliente'),
        ('product', 'Product'),
    ], string='Type Partner Product')
    # type_currency = fields.Selection([
    #     ('sol', 'Nuevo Sol'),
    #     ('dol', 'Dolar'),
    #     ('both', 'Ambas'),
    # ], string='Tipo Moneda')
    fch_start = fields.Date('Fch Inicio')
    fch_end = fields.Date('Fch Final')


    # report
    sale_id = fields.Many2one('sale.order', string='Venta')
    code = fields.Char('Código')
    description_product = fields.Char('Descripción')
    ruc = fields.Char('RUC')
    partner = fields.Char('Cliente')
    kilos = fields.Float('Kilos')

    valor_venta = fields.Float('Valor Venta')
    participacion = fields.Float('% Participación')

    # valor_compra = fields.Float('Costo')

    # utilidad = fields.Float('Utilidad')
    # utilidad_por = fields.Float('%Utilidad')

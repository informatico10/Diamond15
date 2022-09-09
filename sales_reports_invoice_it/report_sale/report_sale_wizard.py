
from pyparsing import line
from odoo import models, fields, api,tools
from datetime import datetime, timedelta
import dateutil.relativedelta


class ReportSaleSelect(models.TransientModel):
    _name = 'report.sale.select.wizard'
    _description ="Report Sale Select Wizard"

    # general
    type_partner_product = fields.Selection([
        ('partner', 'Cliente'),
        ('product', 'Product'),
    ], string='Tipo', default="partner", required=True)
    type_currency = fields.Selection([
        ('sol', 'Nuevo Sol'),
        ('dol', 'Dolar'),
        ('both', 'Ambas'),
    ], string='Tipo Moneda', default="both", required=True)
    fch_start = fields.Date('Fch Inicio', required=True, default=datetime.today() - dateutil.relativedelta.relativedelta(months=1))
    fch_end = fields.Date('Fch Final', required=True, default=datetime.today())

    partner_id = fields.Many2one('res.partner', string='Cliente')
    product_id = fields.Many2one('product.product', string='Producto')
    name = fields.Char(
        string='Name', 
        required=False)

    visualizacion = fields.Selection([
        ('display', 'Pantalla'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ], string='Visualizacion', default="display", required=True)

    # BY REPORT PDF
    # sale_report_partner_product_ids = fields.Many2many('report.sale.select', string='Sale REport PArtner Product')
    company_id = fields.Many2one('res.company', string='company', default=lambda self: self.env.company.id)

    def get_report(self):
        # para q tome la fecha del dia actual a las 00 horas
        self.fch_end = self.fch_end + dateutil.relativedelta.relativedelta(days=1)

        if self.type_partner_product == 'partner':
            self.env.cr.execute("""DROP TABLE IF EXISTS report_sale_select;""")
            self.env.cr.execute("""CREATE TABLE report_sale_select as (""" + self._get_report_by_partner() + """)""")
        elif self.type_partner_product == 'product':
            self.env.cr.execute("""DROP TABLE IF EXISTS report_sale_select;""")
            self.env.cr.execute("""CREATE TABLE report_sale_select as (""" + self._get_report_by_product() + """)""")

        self.fch_end = self.fch_end - dateutil.relativedelta.relativedelta(days=1)
        if self.visualizacion == 'display':
            return {
                'name': 'Ventas Por Cliente/Producto',
                'res_model': 'report.sale.select',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_mode': 'tree'
            }
        elif self.visualizacion == 'pdf':
            self.sale_report_partner_product_ids = self.env['report.sale.select'].search( [] )

            return self.env.ref('sales_reports_invoice_it.action_sale_report_partner_product_diamond').report_action(self)


    def _get_report_by_partner(self):
        ventas_by_partner = self.env['sale.order'].search([('partner_id', '=', self.partner_id.id), ('create_date', '>', self.fch_start), ('create_date', '<', self.fch_end)])

        total_ventas = 0
        for venta in ventas_by_partner:
            total_ventas += venta.amount_untaxed

        currency = ''
        if self.type_currency == 'sol':
            currency = "('PEN')"
        elif self.type_currency == 'dol':
            currency = "('USD')"
        elif self.type_currency == 'both':
            currency = "('USD', 'PEN')"

        sql = """SELECT row_number() OVER () AS id,
                'partner' AS type_partner_product,
				sale_order.id AS sale_id,
                '%s' AS fch_start,
                '%s' AS fch_end,
                product_template.default_code AS code,
                product_template.name AS description_product,
                res_partner.name AS partner,
                res_partner.vat AS ruc,
                sale_order_line.product_uom_qty AS kilos,
                sale_order_line.price_subtotal AS valor_venta,
                CASE
                    WHEN %s != 0 THEN (sale_order_line.price_subtotal * 100) / %s
                    ELSE 0
                END AS participacion

				FROM sale_order_line
				LEFT JOIN sale_order ON sale_order.id = sale_order_line.order_id
                LEFT JOIN product_product on sale_order_line.product_id = product_product.id
                LEFT JOIN product_template on product_product.product_tmpl_id = product_template.id
				LEFT JOIN res_partner ON res_partner.id = sale_order.partner_id
				LEFT JOIN res_currency ON res_currency.id = sale_order.currency_id
                WHERE res_currency.name in %s AND res_partner.id = %s AND sale_order.create_date >= '%s' AND sale_order.create_date <= '%s'
			""" %( self.fch_start.strftime('%Y/%m/%d'), self.fch_end.strftime('%Y/%m/%d'),
                total_ventas, total_ventas, currency, self.partner_id.id, self.fch_start.strftime('%Y/%m/%d'), self.fch_end.strftime('%Y/%m/%d'))

        return sql

    def _get_report_by_product(self):
        line_sale = self.env['sale.order.line'].search([('product_id', '=', self.product_id.id), ('create_date', '>', self.fch_start), ('create_date', '<', self.fch_end)])

        total_ventas = 0
        for venta in line_sale:
            total_ventas += venta.price_subtotal

        currency = ''
        if self.type_currency == 'sol':
            currency = "('PEN')"
        elif self.type_currency == 'dol':
            currency = "('USD')"
        elif self.type_currency == 'both':
            currency = "('USD', 'PEN')"

        sql = """SELECT row_number() OVER () AS id,
                'partner' AS type_partner_product,
				sale_order.id AS sale_id,
                '%s' AS fch_start,
                '%s' AS fch_end,
                product_template.default_code AS code,
                product_template.name AS description_product,
                res_partner.name AS partner,
                res_partner.vat AS ruc,
                sale_order_line.product_uom_qty AS kilos,
                sale_order_line.price_subtotal AS valor_venta,
                CASE
                    WHEN %s != 0 THEN (sale_order_line.price_subtotal * 100) / %s
                    ELSE 0
                END AS participacion

				FROM sale_order_line
				LEFT JOIN sale_order ON sale_order.id = sale_order_line.order_id
                LEFT JOIN product_product on sale_order_line.product_id = product_product.id
                LEFT JOIN product_template on product_product.product_tmpl_id = product_template.id
				LEFT JOIN res_partner ON res_partner.id = sale_order.partner_id
				LEFT JOIN res_currency ON res_currency.id = sale_order.currency_id

                WHERE res_currency.name in %s AND product_product.id = %s AND sale_order.create_date >= '%s' AND sale_order.create_date <= '%s'
			""" %( self.fch_start.strftime('%Y/%m/%d'), self.fch_end.strftime('%Y/%m/%d'),
                total_ventas, total_ventas, currency, self.product_id.id, self.fch_start.strftime('%Y/%m/%d'), self.fch_end.strftime('%Y/%m/%d'))

        return sql

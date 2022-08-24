
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
    product_id = fields.Many2one('product.product', string='Product')

    visualizacion = fields.Selection([
        ('display', 'Pantalla'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ], string='visualizacion', default="display")

    def get_report(self):
        if self.visualizacion == 'display':
            if self.type_partner_product == 'partner':
                self.env.cr.execute("""DROP TABLE IF EXISTS report_sale_select;""")
                self.env.cr.execute("""CREATE TABLE report_sale_select as (""" + self._get_report_by_partner() + """)""")

    def _get_report_by_partner(self):
        fch_ahora = datetime.now() + timedelta(days=1)
        first_date = date(fch_ahora.year, 1, 1)
        sql = """SELECT row_number() OVER () AS id,
				gma.fecha_emi,
				gs2.voucher,
				gma.fecha_ven, gma.cuenta, gma.divisa, gma.tdp,
				gma.doc_partner, gma.partner, gma.td_sunat, gma.nro_comprobante,
				aac.name AS nmbr_cuenta,
				gma.saldo_mn, gma.saldo_me, ac.glosa, ac.invoice_date_due as fch_ven,
                ac.currency_rate as tasa_cambio,
                ac.credit,
                ac.debit,
                ac.pdf_powerbi as pdf,
                ec01.description as tipo_documento,
                cero_treinta, treinta1_sesenta,
				sesenta1_noventa, noventa1_ciento20, ciento21_ciento50,
				ciento51_ciento80, ciento81_mas
				FROM get_maturity_analysis('%s','%s',%s,'%s') as gma
                -- LEFT JOIN account_move AS ac ON gma.nro_comprobante = ac.ref
                LEFT OUTER JOIN LATERAL
                    ( SELECT ac.glosa, ac.invoice_date_due, ac.currency_rate,
                        ac.credit,
                        ac.debit,
                        ac.pdf_powerbi,
                        ac.type_document_id
                        FROM account_move AS ac
                        WHERE gma.nro_comprobante = ac.ref
                        LIMIT 1
                    ) AS ac ON TRUE
				LEFT JOIN account_account AS aac ON aac.code = cuenta
                LEFT OUTER JOIN LATERAL
                    ( SELECT gs2.voucher
                        FROM get_saldos_2('%s', '%s', 1) AS gs2
                        WHERE gs2.nro_comprobante = gma.nro_comprobante
                        LIMIT 1 
                    ) AS gs2 ON TRUE
                LEFT JOIN einvoice_catalog_01 AS ec01 ON ec01.id = ac.type_document_id
                WHERE left(gma.cuenta,2) = '12' OR left(gma.cuenta,2) = '13'
				OR left(gma.cuenta,2) = '14' OR left(gma.cuenta,2) = '16' OR left(gma.cuenta,2) = '17'
			""" %(first_date.strftime('%Y/%m/%d'), fch_ahora.strftime('%Y/%m/%d'), 1, 'receivable', first_date.strftime('%Y/%m/%d'),
                    fch_ahora.strftime('%Y/%m/%d'))
                # -- LEFT JOIN get_saldos_2('%s', '%s',1)
				# -- AS gs2 ON gs2.nro_comprobante = gma.nro_comprobante

        return sql
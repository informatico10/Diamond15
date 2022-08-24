# -*- coding: utf-8 -*-

from pyparsing import line
from odoo import models, fields, api,tools
from datetime import datetime, timedelta


class report_products_invoice(models.Model):
    _name = 'report.products.invoice'
    _description ="Reporte de facturas "
    _auto = False

    razon_social = fields.Char('Cliente')
    codigo = fields.Char('Código')
    product_name	= fields.Char('Descripción')

    invoice_name 	= fields.Char('#Factura')
    invoice_number 	= fields.Char('Nro. Doc')

    fch_emision = fields.Date(string='Fch Emisión')
    fch_entrega = fields.Date(string='Fch Entrega')

    cond_pago = fields.Char('Cond. Pago')
    # cond_pago_sistema = fields.Char('Cond. Pago Sistema')

    fch_vencimiento = fields.Date(string='Fch Vencimiento')
    gr= fields.Char('GR')
    oc = fields.Char('OC')

    # qty_expo = fields.Float('Cantidad Expo',digits=(12,2))
    qty_loc = fields.Float('Cantidad Loc',digits=(12,2))


    price_unit	 	= fields.Float('Precio Unit.',digits=(12,2))

    subtotal_mn        = fields.Monetary('Subtotal MN')
    subtotal_me        = fields.Monetary('Subtotal ME')
    total_mn        = fields.Monetary('Total MN')
    total_me        = fields.Monetary('Total ME')

    iqbf = fields.Boolean('IQBF Internal')
    iqbf_c = fields.Char('IQBF', compute='get_moneda')
    sunat_status = fields.Char('Sunat Status')
    observacion = fields.Char('Observación')

    currency_id = fields.Many2one('res.currency', string='Moneda Id')
    currency_name 	= fields.Char('Moneda')
    tc = fields.Float('TC')
    payment_state = fields.Selection([
        ('not_paid', 'No Pagadas'),
        ('in_payment', 'En proceso de Pago'),
        ('paid', 'Pagado'),
        ('partial', 'Pagado Parcialmente'),
        ('reversed', 'Revertido'),
        ('invoicing_legacy', 'Factura Sistema Anterior'),
    ], string='Estado Pago')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Publicado'),
        ('cancel', 'Cancelado'),
    ], string='Estado')


    # subtotal_amount = fields.Monetary('Sub Total')
    # company_id = fields.Many2one('res.company', 'Company')
    # almacen_id = fields.Many2one('stock.warehouse', string='Almacén')
    # almacen = fields.Char(string='Almacén')

    moneda_mn = fields.Many2one('res.currency', string='Moneda', compute='get_moneda')
    moneda_me = fields.Many2one('res.currency', string='Moneda', compute='get_moneda')

    def get_moneda(self):
        for i in self:
            i.moneda_mn = 154
            i.moneda_me = 2
            if i.iqbf:
                i.iqbf_c = 'X'
            else:
                i.iqbf_c = ''


    # new fields
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
                # account_move_line.price_subtotal as subtotal_amount,
                # account_move_line.price_total as total_amount,
        self._cr.execute("""
            CREATE or REPLACE view %s AS (
                SELECT
                row_number() OVER() AS id, T.* FROM(
                SELECT
                res_partner.name AS razon_social,
                product_product.default_code AS codigo,
                product_template.name AS product_name,
                account_move.name AS invoice_name,
                account_move.ref AS invoice_number,
                account_move.invoice_date AS fch_emision,
                account_move.fch_entrega AS fch_entrega,
                account_payment_term.name AS cond_pago,
                account_move.fch_vencimiento AS fch_vencimiento,
                account_move.gr AS gr,
                account_move.l10n_pe_dte_service_order AS oc,
                -- AS qty_expo
                account_move_line.quantity AS qty_loc,

                account_move_line.price_unit as price_unit,

                CASE
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_subtotal * -1)
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = '$' THEN (account_move_line.price_subtotal * -1 * account_move.currency_rate)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_subtotal)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = '$' THEN (account_move_line.price_subtotal * account_move.currency_rate)
                END as subtotal_mn,
                CASE
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_subtotal * -1 / account_move.currency_rate)
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = '$' THEN (account_move_line.price_subtotal * -1)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_subtotal / account_move.currency_rate)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = '$' THEN (account_move_line.price_subtotal)
                END as subtotal_me,

                CASE
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_total * -1)
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = '$' THEN (account_move_line.price_total * -1 * account_move.currency_rate)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_total)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = '$' THEN (account_move_line.price_total * account_move.currency_rate)
                END as total_mn,
                CASE
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_total * -1 / account_move.currency_rate)
                    WHEN l10n_latam_document_type.code = '07' AND res_currency.symbol = '$' THEN (account_move_line.price_total * -1)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = 'S/' THEN (account_move_line.price_total / account_move.currency_rate)
                    WHEN l10n_latam_document_type.code != '07' AND res_currency.symbol = '$' THEN (account_move_line.price_total)
                END as total_me,

                product_template.iqbf AS iqbf,
                CASE
                    WHEN account_move.state = 'posted' THEN 'Conforme' ELSE '--'
                END AS sunat_status,
                account_move.observacion AS observacion,

                res_currency.id as currency_id,
                res_currency.symbol as currency_name,
                account_move.currency_rate as tc,
                account_move.payment_state as payment_state,
                account_move.state as state

                from account_move_line
                LEFT join account_move on account_move.id = account_move_line.move_id
                LEFT join account_payment_term on account_move.invoice_payment_term_id = account_payment_term.id
                LEFT join product_product on account_move_line.product_id = product_product.id
                LEFT join product_template on product_product.product_tmpl_id = product_template.id
                LEFT join res_partner on account_move.partner_id =res_partner.id
                left join res_currency on account_move.currency_id = res_currency.id
                LEFT join l10n_latam_document_type on account_move.l10n_latam_document_type_id = l10n_latam_document_type.id

                WHERE account_move_line.exclude_from_invoice_tab = false
                    AND  account_move.state = 'posted' AND
                    (account_move.move_type = 'out_invoice' or account_move.move_type = 'out_refund' or account_move.move_type = 'out_receipt')
                )T
            );

        """ % (self._table))

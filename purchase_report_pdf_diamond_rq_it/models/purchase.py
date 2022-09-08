from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date
from . import read_num, read_num_english


class ByDiamond(models.Model):
    _name = 'by.diamond'
    _description = 'By Diamond'

    name = fields.Char('Nombre')


class LoadingPortDiamond(models.Model):
    _name = 'loading.port.diamond'
    _description = 'Loading Port Diamond'

    name = fields.Char('Nombre')


class ShipmentDiamond(models.Model):
    _name = 'shipment.diamond'
    _description = 'Shipment Diamond'

    name = fields.Char('Nombre')


class InsuranceDiamond(models.Model):
    _name = 'insurance.diamond'
    _description = 'Insurance Diamond'

    name = fields.Char('Nombre')


class PurchaseOrderReportPdf(models.Model):
    _inherit = 'purchase.order'

    by_diamond_id = fields.Many2one('by.diamond', string='By / Via')
    type_of_transport = fields.Char('Tipo de Transporte')
    origin_gv = fields.Char('Origen')
    delivery_diaomnd = fields.Html('Delivery terms / Condiciones de entrega', default="""
        CIF - CALLAO ALL IN 2020 <br />
        14 Days free at destination. <br />
        SGS TEST THE SAMPLE
    """)
    marks = fields.Html('Marks')
    quotation = fields.Html('Quotation N', default="""
        Proforma Invoice:
    """)
    loading_port_id = fields.Many2one('loading.port.diamond', string='Loading Port / Puerto de embarque')
    shipment_id = fields.Many2one('shipment.diamond', string='Shipment / Embarque')
    insurance_id = fields.Many2one('shipment.diamond', string='Insurance / Seguro')
    user_approve_firma = fields.Many2one('res.users', string='Usuario Reporte Aprueba', default=lambda self: self.env['res.users'].search( [('name', '=', 'PIERO GIOVANNI LANZA MAURTUA')], limit=1 ).id)

    observaciones = fields.Html('Observaciones', default="""
        <b>Observaciones</b>
        <br />
        DESPACHAR EN: CALLE LAS GARDENIAS MZ D LT. 16 KM 40 PAN SUR ANTIGUA
        <br />
        INDICAR EN LA GUÍA Y FACTURA NUESTRO NÚMERO DE OC
        <br />
        ENTREGAR: MSDS, CERTIFICADO DE ANÁLISIS, NÚMERO DE LOTE, FECHA DE PRODUCCIÓN
    """)

    total_spanish = fields.Char('Total Spanish')
    total_english = fields.Char('Total English')

    incoterm_diamond = fields.Selection([
        ('0', 'FOB'),
        ('1', 'FCA'),
        ('2', 'CIF'),
        ('3', 'EXwork'),
    ], string='Incoterm', readonly=True)
    incoterm_country_diamond_id = fields.Many2one('res.country', string='Incoterm País', readonly=True)
    check_incoterm = fields.Boolean(compute='_compute_check_incoterm', string='Check Incoterm')

    @api.depends('incoterm_diamond', 'incoterm_country_diamond_id')
    def _compute_check_incoterm(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.is_supplier:
                rec.incoterm_diamond = rec.partner_id.incoterm_diamond
                rec.incoterm_country_diamond_id = rec.partner_id.incoterm_country_diamond_id
            else:
                rec.incoterm_diamond = False
                rec.incoterm_country_diamond_id = False
            rec.check_incoterm = True

            rec.total_spanish = read_num.numero_a_monedas(rec.amount_total)
            rec.total_english = read_num_english.numero_a_monedas(rec.amount_total)

    motivo_oc = fields.Selection([
        ('0', 'OC'),
        ('1', 'OS'),
        ('2', 'OSQ'),
    ], string='Motivo de OC')

    infra_project = fields.Text('Proyecto Infraestructura')

    fch_aprobacion = fields.Date('Fecha de Aprobación', tracking=True)
    user_aprobacion_id = fields.Many2one('res.users', string='Usuario que Aprobo', tracking=True)

    def button_confirm(self):
        res = super(PurchaseOrderReportPdf, self).button_confirm()
        self.fch_aprobacion = date.today()
        self.user_aprobacion_id = self.env.user.id
        return res

    def button_cancel(self):
        res = super(PurchaseOrderReportPdf, self).button_cancel()
        self.fch_aprobacion = False
        self.user_aprobacion_id = False
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(PurchaseOrderReportPdf, self).create(vals)
        if res.partner_id and res.partner_id.country_id and res.partner_id.country_id.name != 'Perú':
            id_seq = self.env['ir.sequence'].sudo().search([('name','=','Compra Importacion Secuencia Diamond')], limit=1)

            if not id_seq:
                id_seq = self.env['ir.sequence'].sudo().create({
                    'name': 'Compra Importacion Secuencia Diamond',
                    'implementation': 'no_gap',
                    'active': True,
                    'prefix': 'PO-I-10-',
                    'padding': 4,
                    'number_increment': 1,
                    'number_next_actual': 1
                })
            self.name = id_seq._next()
            res.name = id_seq._next()

            if res.marks == '' or res.marks == False:
                res.marks = res.name + '<br /> DIAMOND CORPORACION S.A'

        return res

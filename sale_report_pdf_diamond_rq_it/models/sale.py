from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleLinePresentation(models.Model):
    _name = 'sale.line.presentation'
    _description = 'Sale Line Presentation'

    name = fields.Char('Presentación')


class SaleOrderLineSaleReport(models.Model):
    _inherit = 'sale.order.line'

    presentation_id = fields.Many2one('sale.line.presentation', string='Presentación')


class SaleOrderReportPdf(models.Model):
    _inherit = 'sale.order'

    #to contact
    id_partner_to_create = fields.Integer(string='', related='partner_id.id')
    street_partner = fields.Char(string='', related='partner_id.street')
    # street2_partner = fields.Char(string='', related='partner_id.street2')
    city_partner = fields.Char(string='', related='partner_id.city')
    state_partner = fields.Many2one('res.country.state', string='', related='partner_id.state_id')
    zip_partner = fields.Char(string='', related='partner_id.zip')
    country_partner = fields.Many2one('res.country', string='', related='partner_id.country_id')

    referencia_pdf = fields.Text(string='Referencia')
    first_contacto_partner = fields.Many2one('res.partner', string='Atención')
    ids_first_contact = fields.Many2many('res.partner', string='domain by first contact')

    check_domain = fields.Boolean(compute='_compute_check_domain', string='Check Domain')

    @api.depends('ids_first_contact')
    def _compute_check_domain(self):
        for rec in self:
            # TO DOMAIN FIRST CONTACT
            if rec.partner_id:
                ar_child = []
                for child in rec.partner_id.child_ids:
                    if child.type == 'contact':
                        ar_child.append(child.id)
                rec.ids_first_contact = ar_child


    @api.onchange('partner_id')
    def _onchange_partner_id_order_report(self):
        for rec in self:
            if self.partner_id:
                ar_child = []
                for child in self.partner_id.child_ids:
                    if child.type == 'contact':
                        ar_child.append(child.id)
                return {
                    'domain': {
                        'first_contacto_partner': [('id', 'in', ar_child)]
                    }
                }

    note_report = fields.Html(string='Terminos y condiciones', default="""
        <b>* PRECIO: NO INCLUYE IGV</b>
        <br />
        <br />
        <b>CONDICIONES DE PAGO</b>: Factura 45 días.
        
        1 Vigencia de la cotización:
        <br />
        2 Valor expresado:
        <br />
        3 Forma de pago:
        <br />
        4 Plazo de entrega:
        <br />
        5 Garantía:
        <br />
        6 Tipo de cambio:

        PRESENTACIÓN: Big Bag X 600 Kg., en cada paleta se colocarán 2 Big Bag X 600 Kg. c/u, es decir cada paleta cargará
        1,200 Kg.
        ENTREGA: A partir del 15 de agosto. Sujeto a confirmación de equipo (contenedor, nave, etc)
        LUGAR DE ENTREGA: En nuestro almacén de Lurín
        VALIDEZ: 17/05/2022 al terminar el día (17 horas)
        NOTA:
        • La cantidad ofrecida está sujeta a disponibilidad por venta.
        A la espera de sus gratas órdenes, me despido.
        Atentamente,
    """)

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


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
        <br /><br />
        <b>CONDICIONES DE PAGO:</b> Factura 45 días.
        <br /><br />
        <b>PRESENTACIÓN:</b> Big Bag X 600 Kg., en cada paleta se colocarán 2 Big Bag X 600 Kg. c/u, es decir cada paleta cargará
        1,200 Kg.
        <br /><br />
        <b>ENTREGA:</b> A partir del 15 de agosto. Sujeto a confirmación de equipo (contenedor, nave, etc)
        <br /><br />
        <b>LUGAR DE ENTREGA:</b> En nuestro almacén de Lurín
        <br /><br />
        <b>VALIDEZ:</b> 17/05/2022 al terminar el día (17 horas)
        <br /><br />
        <b>NOTA:</b>
            • La cantidad ofrecida está sujeta a disponibilidad por venta.
        <br /><br />
        A la espera de sus gratas órdenes, me despido.
        <br /><br />

        Atentamente,
    """)

    @api.model_create_multi
    def create(self, vals):
        id_seq = self.env['ir.sequence'].sudo().search([('name','=','Venta Secuencia Diamond')], limit=1)
        if not id_seq:
            id_seq = self.env['ir.sequence'].sudo().create({
                'name': 'Venta Secuencia Diamond',
                'implementation': 'no_gap',
                'active': True,
                'prefix': '',
                'padding': 4,
                'number_increment': 1,
                'number_next_actual': 1
            })

        first = 'DG '
        second = ''
        today_month = str(datetime.today().month)
        today_year = str(datetime.today().year)

        if len(str(today_month)) == 1:
            second = '0' + today_month
        elif len(str(today_month)) == 2:
            second = today_month
        today_year = today_year[2:]
        second += today_year + '-'

        sequence = id_seq._next()
        name = first + second + sequence
        res = super(SaleOrderReportPdf,self).create(vals)
        res.name = name
        return res

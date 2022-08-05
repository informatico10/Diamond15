from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderValidationCreation(models.Model):
    _inherit = 'sale.order'


    @api.model_create_multi
    def create(self, vals):
        res = super(SaleOrderValidationCreation, self).create(vals)
        if res.partner_id:
            message = ''
            if res.partner_id.name == False or res.partner_id.name == '':
                message += 'Cliente no tiene Nombre \n'
            if res.partner_id.vat == False or res.partner_id.vat == '':
                message += 'Cliente no tiene VAT (RUC, DNI, etc) \n'
            if res.partner_id.street == False or res.partner_id.street == '':
                message += 'Cliente no tiene registrado el campo Calle \n'
            if res.partner_id.city == False or res.partner_id.city == '':
                message += 'Cliente no tiene registrado el campo Ciudad \n'
            if res.partner_id.state_id == False:
                message += 'Cliente no tiene registrado el campo Departamento \n'
            if res.partner_id.province_id == False:
                message += 'Cliente no tiene registrado el campo Provincia \n'
            if res.partner_id.district_id == False:
                message += 'Cliente no tiene registrado el campo Distrito \n'
            if res.partner_id.email == False or res.partner_id.email == '':
                message += 'Cliente no tiene Email\n'
            if res.partner_id.user_id == False:
                message += 'Cliente no tiene Vendedor Asociado\n'
            if message != '':
                raise ValidationError('Cliente no valido \n\n' + message)
        return res


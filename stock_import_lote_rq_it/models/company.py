from odoo import models, fields, api
from odoo.exceptions import ValidationError
from xlrd import open_workbook
import base64


class ResCompanyImportLoteRqIT(models.Model):
    _inherit = 'res.company'

    sale_template_import_only_product = fields.Binary('Plantilla Importador Solo 1 Producto')
    name_sale_template_import_only_product = fields.Char('Nombre Archivo Importar')
    sale_template_import_multi_product = fields.Binary('Plantilla Importador Multi Producto')
    name_sale_template_import_multi_product = fields.Char('Nombre Archivo a Importar')

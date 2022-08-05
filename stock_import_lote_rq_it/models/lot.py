from odoo import models, fields, api
from odoo.exceptions import ValidationError
from xlrd import open_workbook
import base64


class StockProductionLotImportRQ(models.Model):
    _inherit = 'stock.production.lot'

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            search = self.env['stock.production.lot'].search( [('name', '=ilike', rec.name), ('company_id', '=', rec.company_id.id)] )
            if len(search) > 1:
                raise ValidationError('No puede tener series duplicadas, ya existe serie/lote con nombre <' + rec.name + '>')


class LotDuplicate(models.TransientModel):
    _name = 'lot.duplicate'

    action_import = fields.Boolean('Action Import', readonly=True)
    file_import = fields.Binary('Archivo a Importar')
    name_file_import = fields.Char('Nombre Archivo a Importar')

    company_id = fields.Many2one('res.company', string='company', default=lambda self: self.env.company)
    template_file = fields.Binary('Plantilla a Importar', default=lambda self: self.env.company.sale_template_import_multi_product)
    name_template_file = fields.Char('Nombre Plantilla a Importar', default=lambda self: self.env.company.name_sale_template_import_multi_product)

    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    mensaje = fields.Char('Mensaje')
    cant_import = fields.Char('Cantidad Importados')
    # lot_ids = fields.Many2many('stock.production.lot', string='lot')
    lot_duplicate_picking_id = fields.Many2many('lot.duplicate.picking', string='Ubicación Lote/serie')

    def download_template(self):
        import base64
        # result = base64.b64encode(self.template_file)
        result = self.template_file
        # get base url
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        # create attachment
        attachment_id = attachment_obj.create(
            {'name': self.name_template_file, 'datas': result})
        # prepare download url
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # download
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    def import_lot_product(self):
        if self.name_file_import.find('.xlsx') > -1:
            wb = False
            try:
                wb = open_workbook(file_contents = base64.b64decode(self.file_import))
            except:
                raise ValidationError('Archivo no tiene formato Excel (.xlsx)')
            sheet = wb.sheets()[0]

            product_duplicated = []
            product_no_exist = []
            for s in wb.sheets():
                for row in range(s.nrows):
                    if row != 0:
                        product_excel = s.cell(row, 0).value
                        product = self.env['product.product'].search([('name', '=', product_excel), ('company_id', 'in', [self.company_id.id, False])])
                        if len(product) == 0:
                            product_no_exist.append(product_excel)
                        elif len(product) > 1:
                            product_duplicated.append(product_excel)

            if len(product_duplicated) > 0 or len(product_no_exist):
                message = 'ERROR \n'
                if len(product_duplicated) > 0:
                    message += 'Productos Duplicados: '
                    for pr in product_duplicated:
                        message += pr + ', '
                    message = message[:-2]
                    message += '\n'

                if len(product_no_exist) > 0:
                    message += 'Productos No existentes: '
                    for pr in product_no_exist:
                        message += pr + ', '
                    message = message[:-2]
                    message += '\n'
                raise ValidationError(message)


            no_import_serie = []
            count_import = 0
            count_no_import = 0

            for s in wb.sheets():
                for row in range(s.nrows):
                    if row != 0:
                        product_excel = s.cell(row, 0).value
                        producto = self.env['product.product'].search([('name', '=', product_excel), ('company_id', 'in', [self.company_id.id, False])])

                        serie = s.cell(row, 1).value
                        cant_serie = s.cell(row, 2).value
                        if producto.tracking == 'serial':
                            if cant_serie > 1:
                                cant_serie = 1

                        search = self.env['stock.production.lot'].search( [('name', '=ilike', serie), ('company_id', '=', self.company_id.id)] )

                        search_stock_move_line = self.env['stock.move.line'].search( [('lot_name', '=ilike', serie), ('company_id', '=', self.company_id.id)] )

                        if len(search) == 0 and len(search_stock_move_line) == 0:
                            new_lot = self.env['stock.production.lot'].create({
                                'name': serie,
                                'product_qty': cant_serie,
                                'product_id': product.id,
                                'company_id': self.company_id.id
                            })
                            count_import += 1
                        else:
                            if len(search_stock_move_line) > 0:
                                for stock_line in search_stock_move_line:
                                    new_id = self.env['lot.duplicate.picking'].create( {
                                        'name_lot': serie,
                                        'picking_id': stock_line.move_id.picking_id.id if stock_line.move_id.picking_id else False,
                                        'product_id': product.id,
                                        'stock_move_id': stock_line.move_id.id if stock_line.move_id else False,
                                        'lot_id': False if len(search) == 0 else search[0].id
                                    } )
                                    no_import_serie.append(new_id.id)
                            elif len(search) > 0:
                                new_id = self.env['lot.duplicate.picking'].create( {
                                    'name_lot': serie,
                                    'picking_id': False,
                                    'stock_move_id': False,
                                    'lot_id': search[0].id
                                } )
                                no_import_serie.append(new_id.id)
                            count_no_import += 1

            mensaje_count = 'Importados: ' + str(count_import) + '   /   ' + 'No Importados ' + str(count_no_import)

            mensaje = 'Series/Lotes ya existentes que no se pueden importar'
            return {
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'lot.duplicate',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_action_import': False,
                    'default_lot_duplicate_picking_id': no_import_serie,
                    'default_cant_import': mensaje_count,
                    'default_mensaje': mensaje,
                    'default_stock_move_id': self.id
                }
            }


class LotDuplicateStock(models.TransientModel):
    _name = 'lot.duplicate.picking'

    name_lot = fields.Char('Nombre Lote')
    product_id = fields.Many2one('product.product', string='Producto')
    picking_id = fields.Many2one('stock.picking', string='Uso en Transferencia')
    stock_move_id = fields.Many2one('stock.move', string='Uso en Movimiento')
    lot_id = fields.Many2one('stock.production.lot', string='Existencia Lote')

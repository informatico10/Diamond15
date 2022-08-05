from odoo import models, fields, api
from odoo.exceptions import ValidationError
from xlrd import open_workbook
import base64


class StockPickingImportLoteRqIT(models.Model):
    _inherit = 'stock.picking'

    def action_import_lot(self):
        return {
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'lot.duplicate',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_action_import': True,
            }
        }


class StockMoveImportRqIt(models.Model):
    _inherit = 'stock.move'

    operation_type = fields.Selection(string='Tipo de Operación', related='picking_id.picking_type_id.code')
    file_import = fields.Binary('Archivo a Importar')
    name_file_import = fields.Char('Nombre Archivo a Importar')

    template_file = fields.Binary('Plantilla a Importar', related='company_id.sale_template_import_only_product')
    name_template_file = fields.Char('Nombre Plantilla a Importar', related='company_id.name_sale_template_import_only_product')

    def import_lot_only_product(self):
        if self.name_file_import.find('.xlsx') > -1:
            wb = False
            try:
                wb = open_workbook(file_contents = base64.b64decode(self.file_import))
            except:
                raise ValidationError('Archivo no tiene formato Excel (.xlsx)')
            sheet = wb.sheets()[0]

            no_import_serie = []
            count_import = 0
            count_no_import = 0

            for s in wb.sheets():
                for row in range(s.nrows):
                    if row != 0:
                        serie = s.cell(row, 0).value
                        cant_serie = s.cell(row, 1).value
                        if self.product_id.tracking == 'serial':
                            if cant_serie > 1:
                                cant_serie = 1

                        search = self.env['stock.production.lot'].search( [('name', '=ilike', serie), ('company_id', '=', self.company_id.id)] )

                        search_stock_move_line = self.env['stock.move.line'].search( [('lot_name', '=ilike', serie), ('company_id', '=', self.company_id.id)] )

                        if self.operation_type == 'incoming':
                            if len(search) == 0 and len(search_stock_move_line) == 0:
                                self.move_line_nosuggest_ids += self.env['stock.move.line'].create({
                                    'lot_name': serie,
                                    'qty_done': cant_serie,
                                    'product_uom_id': self.product_uom.id,
                                    'product_id': self.product_id.id,
                                    'move_id': self.id,
                                    'picking_id': self.picking_id.id,
                                    'company_id': self.company_id.id
                                })
                                count_import += 1
                            else:
                                if len(search_stock_move_line) > 0:
                                    for stock_line in search_stock_move_line:
                                        new_id = self.env['lot.duplicate.picking'].create( {
                                            'name_lot': serie,
                                            'picking_id': stock_line.move_id.picking_id.id if stock_line.move_id.picking_id else False,
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
                        else:
                            if len(search) == 0 and len(search_stock_move_line) == 0:
                                self.move_line_nosuggest_ids += self.env['stock.move.line'].create({
                                    'lot_id': search[0].id,
                                    'qty_done': cant_serie,
                                    'product_uom_id': self.product_uom.id,
                                    'product_id': self.product_id.id,
                                    'move_id': self.id,
                                    'picking_id': self.picking_id.id,
                                    'company_id': self.company_id.id
                                })
                                count_import += 1
                            else:
                                if len(search_stock_move_line) > 0:
                                    for stock_line in search_stock_move_line:
                                        new_id = self.env['lot.duplicate.picking'].create( {
                                            'name_lot': serie,
                                            'picking_id': stock_line.move_id.picking_id.id if stock_line.move_id.picking_id else False,
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

            mensaje = ""
            if self.operation_type == 'incoming':
                mensaje = 'Series/Lotes ya existentes que no se pueden importar'
            else:
                mensaje = 'Series/Lotes que ya estan usados o no existen'
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
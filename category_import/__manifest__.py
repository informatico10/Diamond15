# -*- encoding: utf-8 -*-
{
	'name': 'Importador Categorias Producto',
	'category': 'stock',
	'author': 'ITGRUPO',
	'depends': ['base','stock'],
	'version': '1.0',
	'description':"""
		Importador Categorias Producto
	""",
	'auto_install': False,
	'demo': [],
	'data': [
		'security/ir.model.access.csv',
        'security/category_import_security.xml',
        'data/attachment_sample.xml',
        'views/category_import_view.xml',        
    ],
	'installable': True
}
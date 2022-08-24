# -*- encoding: utf-8 -*-
{
	'name': 'Reportes para ventas de lavoro',
	'category': 'sale',
	'author': 'ITGRUPO',
	'depends': ['sale', 'account', 'stock', 'logistic', 'account_fields_it'],
	'version': '1.0',
	'description':"""
		REPORTES DE VENTAS Y FACTURAS
		CORRER en acciones planificadas
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
		'views/invoice_reports.xml',
		'views/account_move.xml',
		'views/sale.xml',
		'views/product.xml',

		'report_sale/report_sale_wizard.xml',
	],
	'installable': True
}

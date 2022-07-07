# -*- encoding: utf-8 -*-
{
	'name': 'Reporte de productos en mano compras',
	'category': 'stock',
	'author': 'ITGRUPO',
	'depends': ['stock','purchase'],
	'version': '1.0',
	'description':"""
	Reporte de productosa en mano compras
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		#'security/security.xml',
		'security/ir.model.access.csv',
		'views/stock_report_onhand.xml'
	],
	'installable': True
}

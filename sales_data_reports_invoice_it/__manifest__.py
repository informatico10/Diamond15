# -*- encoding: utf-8 -*-
{
	'name': 'Sales Data Reports Invoice IT',
	'category': 'sale',
	'author': 'ITGRUPO',
	'depends': ['sale', 'account', 'stock', 'logistic', 'account_fields_it', 'l10n_pe_edi_extended'],
	'version': '1.0',
	'description':"""
		Sales Data Reports Invoice IT
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/account_move.xml',
		'views/sale.xml',
		'views/product.xml',
	],
	'installable': True
}

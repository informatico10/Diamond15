# -*- encoding: utf-8 -*-
{
	'name': 'Sales Reports Invoice IT',
	'category': 'sale',
	'author': 'ITGRUPO',
	'depends': ['sale', 'account', 'stock', 'logistic', 'account_fields_it', 'l10n_pe_edi_extended'],
	'version': '1.0',
	'description':"""
		Sales Reports Invoice IT
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
		'views/invoice_reports.xml',

		'report_sale/report_sale_wizard.xml',
		'report_sale/report_sale_model.xml',
		'report_sale/pdf.xml',
	],
	'installable': True
}

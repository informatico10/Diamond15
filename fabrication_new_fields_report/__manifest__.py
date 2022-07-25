# -*- encoding: utf-8 -*-
{
    'name': 'RYA DESARROLLO',
    'category': 'uncategorize',
    'author': 'ITGRUPO',
    'depends': ['mrp_account_enterprise','account_base_it','kardex_mrp_production_jp'],
    'version': '1.0',
    'description':"""
     Descripcion
    """,

    'auto_install': False,
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/mano_obra_tree.xml',
        'views/mano_obra_report.xml',
        ],
    'installable': True
}
{
    'name': 'Stock Import Lote Rq IT',
    'version': '1.0',
    'description': """
        No permite duplicar lotes
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'stock picking',
    'auto_install': False,
    'depends': [
        'stock',
    ],
    'data': [
        'security/security.xml',
        'views/stock_move.xml',
        'views/lot.xml',
        'views/company.xml'
    ],
    'installable': True
}
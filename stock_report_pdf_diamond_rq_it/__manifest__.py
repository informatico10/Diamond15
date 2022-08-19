{
    'name': 'Stock Report PDF Diamond RQ IT',
    'version': '1.0',
    'description': 'Stock Report PDF Diamond RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'sale',
    'auto_install': False,
    'depends': [
        'stock',
    ],
    'data': [
        # 'security/security.xml',

        'reports/stock.xml',
        'views/stock.xml',
    ],
    'installable': True
}

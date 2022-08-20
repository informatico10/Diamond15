{
    'name': 'Sale Payment Rq It',
    'version': '1.0',
    'description': """
        Sale Payment Rq It
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'stock picking',
    'auto_install': False,
    'depends': [
        'sale',
        'account'
    ],
    'data': [
        'security/security.xml',
        'views/payment.xml',
        'views/partner.xml',
        'views/sale.xml',
    ],
    'installable': True
}
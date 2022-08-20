{
    'name': 'Purchase Duas Rq It',
    'version': '1.0',
    'description': """
        Purchase Duas Rq It
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'stock picking',
    'auto_install': False,
    'depends': [
        'purchase',
        'stock',
        'account_purchase_notify_rq_it'
    ],
    'data': [
        'security/security.xml',
        'views/views.xml',
        'views/agency.xml'
    ],
    'installable': True
}
{
    'name': 'Account Purchase Notify Rq It',
    'version': '1.0',
    'description': """
        Account Purchase Notify Rq IT
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'stock picking',
    'auto_install': False,
    'depends': [
        'account',
        'purchase',
        'account_fields_it'
    ],
    'data': [
        'views/purchase.xml',
        'views/account.xml',
    ],
    'installable': True
}
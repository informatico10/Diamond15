{
    'name': 'Stock Notification Rq IT',
    'version': '1.0',
    'description': """
        Stock Notification Rq IT
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'stock picking',
    'auto_install': False,
    'depends': [
        'stock',
        'sale'
    ],
    'data': [
        'security/security.xml',
        'views/user.xml',
    ],
    'installable': True
}
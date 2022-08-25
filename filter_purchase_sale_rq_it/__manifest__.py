{
    'name': 'Filter Purchase Sale RQ IT',
    'version': '1.0',
    'description': """
        Filter Purchase Sale RQ IT
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'sale, purchase',
    'auto_install': False,
    'depends': [
        'sale',
        'purchase',
        'account_fields_it'
    ],
    'data': [
        'views/views.xml',
    ],
    'installable': True
}

{
    'name': 'Purchase Report PDF Diamond RQ IT',
    'version': '1.0',
    'description': 'Purchase Report PDF Diamond RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'sale',
    'auto_install': False,
    'depends': [
        'purchase',
        'account_fields_it'
    ],
    'data': [
        'security/security.xml',

        'views/users.xml',
    ],
    'installable': True
}

{
    'name': 'Purchase Confirm RQ IT',
    'version': '1.0',
    'description': 'Purchase Confirm RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'account',
    'auto_install': False,
    'depends': [
        'purchase',
        'category_only_rq_it'
    ],
    'data': [
        'security/security.xml',

        'views/view.xml'
    ],
    'installable': True
}
{
    'name': 'Account Group RQ IT',
    'version': '1.0',
    'description': 'Account Group RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'account',
    'auto_install': False,
    'depends': [
        'account',
        'account_debit_note',
        'account_purchase_notify_rq_it'
    ],
    'data': [
        'security/security.xml',

        'views/view.xml'
    ],
    'installable': True
}
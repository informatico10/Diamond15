{
    'name': 'Group RQ IT',
    'version': '1.0',
    'description': 'Group RQ IT, añade nuevos permisos para cada modulo',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'account',
    'auto_install': False,
    'depends': [
        'sale',
        'purchase',
        'account',
    ],
    'data': [
        'security/security.xml',

        # 'views/view.xml'
    ],
    'installable': True
}
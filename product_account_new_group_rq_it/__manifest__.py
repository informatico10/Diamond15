{
    'name': 'Product Account New Group RQ IT',
    'version': '1.0',
    'description': 'Product Account New Group RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'product',
    'auto_install': False,
    'depends': [
        'account',
        'category_only_rq_it'
    ],
    'data': [
        'security/security.xml',
        'views/product.xml',
    ],
    'installable': True
}


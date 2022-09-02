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
        'account_fields_it',
        'purchase_stock',
        'account'
    ],
    'data': [
        'security/security.xml',

        'reports/purchase.xml',
        'views/partner.xml',
        'views/purchase_by.xml',
        'views/purchase_insurance.xml',
        'views/purchase_loading.xml',
        'views/purchase_shipment.xml',
        'views/purchase_menu.xml',
        'views/purchase.xml',
    ],
    'installable': True
}

{
    'name': 'Production Report Pdf Diamond RQ IT',
    'version': '1.0',
    'description': 'Production Report Pdf Diamond RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'sale',
    'auto_install': False,
    'depends': [
        'mrp',
        # 'sale_order_report_by_warehouse_it',
    ],
    'data': [
        'security/security.xml',

        'reports/mrp.xml',
        'views/mrp.xml',
    ],
    'installable': True
}

{
    'name': 'Sale Report Pdf Diamond RQ IT',
    'version': '1.0',
    'description': 'Sale Report Pdf Diamond RQ IT',
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'sale',
    'auto_install': False,
    'depends': [
        'sale',
        'company_report_logo_rq_it'
        # 'sale_order_report_by_warehouse_it',
    ],
    'data': [
        'security/security.xml',

        'reports/sale.xml',
        'views/sale.xml',
    ],
    'installable': True
}
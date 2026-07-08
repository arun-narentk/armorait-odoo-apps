# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Revenue KPIs, targets, charts, and sales analytics',
    'description': """
Business Intelligence Sales Dashboard for Odoo 19 Community
===========================================================

Commercial analytics suite for sales teams and managers.

Phase 1 delivers the installable framework: KPI models, targets,
snapshots, filter engine, OWL dashboard shell, Chart.js hooks,
export stubs, and service-layer architecture ready for future
bi_* dashboard modules to share patterns with.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 39.99,
    'sequence': 35,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'sale_management',
        'crm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/dashboard_data.xml',
        'data/ir_config_parameter.xml',
        'views/dashboard_views.xml',
        'views/filter_views.xml',
        'views/settings_views.xml',
        'views/target_views.xml',
        'views/favorite_views.xml',
        'views/menu.xml',
        'report/dashboard_pdf.xml',
        'report/dashboard_xlsx.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_bi_sales_dashboard/static/src/scss/bi_sales.scss',
            'rn_bi_sales_dashboard/static/src/xml/bi_dashboard.xml',
            'rn_bi_sales_dashboard/static/src/js/bi_dashboard.js',
            'rn_bi_sales_dashboard/static/src/js/chart_utils.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/overview.png',
        'static/description/dashboard.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

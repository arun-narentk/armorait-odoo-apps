# -*- coding: utf-8 -*-
{
    'name': 'Restaurant Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Branches, floors, tables, menu, and restaurant setup',
    'description': """
ARMORA Restaurant Core for Odoo 19 Community
============================================

Domain foundation for ARMORA Restaurant Cloud POS.

Phase 1 delivers restaurant and branch configuration, dining areas,
tables, menu categories and items, restaurant taxes, payment methods,
service layer APIs, OWL overview dashboard, and SaaS edition tracking.

Companion modules add POS, KDS, QR ordering, inventory recipes,
delivery, loyalty, online ordering, and AI forecasting.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 46,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'product',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/restaurant_data.xml',
        'data/cron.xml',
        'views/restaurant_views.xml',
        'views/branch_views.xml',
        'views/floor_views.xml',
        'views/table_views.xml',
        'views/menu_views.xml',
        'views/tax_views.xml',
        'views/payment_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/restaurant_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_restaurant_core/static/src/scss/restaurant.scss',
            'rn_restaurant_core/static/src/xml/restaurant_dashboard.xml',
            'rn_restaurant_core/static/src/js/restaurant_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/workflow.png',
        'static/description/dashboard.png',
        'static/description/designer.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

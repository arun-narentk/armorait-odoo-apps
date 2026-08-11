# -*- coding: utf-8 -*-
{
    'name': 'Dashboard KPI Studio',
    'version': '19.0.1.1.0',
    'category': 'Productivity',
    'summary': 'No-code Odoo dashboard builder with KPIs, charts, filters, and layouts',
    'description': """
Dashboard KPI Studio for Odoo 19 Community
==========================================

Original ARMORA dashboard builder for creating KPI tiles, charts, lists, and
interactive layouts from any accessible Odoo model.

Phase 2 delivers the complete backend data model: dashboards, items, filters,
bookmarks, validation, duplication, export definitions, menu helpers, and a
secure ORM data engine for count and grouped aggregations.

Visualization UI enhancements continue in later phases.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 38,
    'depends': [
        'base',
        'mail',
        'web',
        'bus',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/dashboard_views.xml',
        'views/dashboard_item_views.xml',
        'views/dashboard_filter_views.xml',
        'views/dashboard_bookmark_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('include', 'web.chartjs_lib'),
            'rn_dashboard_kpi/static/src/scss/dashboard.scss',
            'rn_dashboard_kpi/static/src/scss/themes.scss',
            'rn_dashboard_kpi/static/src/utils/visualization_registry.js',
            'rn_dashboard_kpi/static/src/services/dashboard_service.js',
            'rn_dashboard_kpi/static/src/dashboard/dashboard_action.js',
            'rn_dashboard_kpi/static/src/xml/dashboard.xml',
        ],
        'web.assets_unit_tests': [
            'rn_dashboard_kpi/static/tests/visualization_registry_tests.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

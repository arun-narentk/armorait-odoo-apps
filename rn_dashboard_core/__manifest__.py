# -*- coding: utf-8 -*-
{
    'name': 'Dashboard Core',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Shared OWL dashboard shell for ARMORA analytics modules',
    'description': """
ARMORA Dashboard Core for Odoo 19 Community
==========================================

Reusable dashboard engine for ARMORA Manufacturing Intelligence and other
analytics suites. Phase 1 delivers dashboard definitions, widgets, filters,
alert rules, KPI snapshots, cache helpers, OWL shell, TV-ready refresh hooks,
subscription edition tracking, and service-layer APIs.

Domain modules such as rn_mrp_dashboard, rn_mrp_oee, and rn_mrp_production_tv
depend on this core instead of duplicating chart, filter, or alert logic.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 40,
    'depends': [
        'base',
        'mail',
        'web',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/dashboard_data.xml',
        'data/cron.xml',
        'views/dashboard_views.xml',
        'views/widget_views.xml',
        'views/filter_views.xml',
        'views/alert_views.xml',
        'views/kpi_views.xml',
        'views/settings_views.xml',
        'views/menu.xml',
        'report/dashboard_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_dashboard_core/static/src/scss/dashboard_core.scss',
            'rn_dashboard_core/static/src/xml/dashboard_shell.xml',
            'rn_dashboard_core/static/src/js/chart_utils.js',
            'rn_dashboard_core/static/src/js/dashboard_shell.js',
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

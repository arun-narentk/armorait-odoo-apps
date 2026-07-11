# -*- coding: utf-8 -*-
{
    'name': 'ERP Health Analyzer',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'AI-assisted ERP intelligence: performance, security, data quality, and upgrade readiness',
    'description': """
ERP Health Analyzer for Odoo 19 Community
=========================================

Not a one-time health check. A continuous ERP intelligence layer that scans
performance, security, data quality, accounting hygiene, module sprawl,
and operational risk.

Phase 1 delivers:

* Scan targets and reusable scan profiles
* Automated ERP findings with severity and score impact
* Executive score dashboard and recent risk feed
* Performance, security, data quality, accounting, and module checks
* Action-ready recommendations for consultants and internal teams
* Human-review-first workflow for AI-assisted remediation planning
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 48,
    'depends': [
        'base',
        'mail',
        'web',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/target_data.xml',
        'views/health_target_views.xml',
        'views/health_scan_views.xml',
        'views/health_finding_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_erp_health_analyzer/static/src/scss/erp_health_analyzer.scss',
            'rn_erp_health_analyzer/static/src/xml/erp_health_dashboard.xml',
            'rn_erp_health_analyzer/static/src/js/erp_health_dashboard.js',
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

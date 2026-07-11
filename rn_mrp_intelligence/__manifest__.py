# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Intelligence',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Factory command center: production KPIs, OEE, WIP, bottlenecks, AI insights',
    'description': """
ARMORA Manufacturing Intelligence for Odoo 19 Community
=======================================================

Real-time operational command center for factory managers and directors.

Phase 1 (rn_mrp_intelligence) delivers:

* Executive summary KPIs (production, delays, utilization, WIP, scrap)
* Production dashboard (planned vs actual, daily/weekly/monthly output)
* Work center and machine status (running, idle, breakdown, maintenance)
* OEE tracking (availability, performance, quality)
* Downtime logs and bottleneck detection hooks
* Shift comparison (A/B/C) framework
* Inventory and purchase risk KPIs from stock and PO data
* AI factory summary and insight records
* OWL dashboard with role-ready KPI cards

Roadmap: predictive maintenance, AI chat, energy dashboard, mobile TV mode,
multi-plant consolidation, quality and maintenance deep dives.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 50,
    'depends': [
        'base',
        'mail',
        'web',
        'mrp',
        'stock',
        'purchase',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/shift_views.xml',
        'views/downtime_views.xml',
        'views/oee_views.xml',
        'views/insight_views.xml',
        'views/workcenter_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_mrp_intelligence/static/src/scss/mrp_intelligence.scss',
            'rn_mrp_intelligence/static/src/xml/mrp_dashboard.xml',
            'rn_mrp_intelligence/static/src/js/mrp_dashboard.js',
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

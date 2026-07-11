# -*- coding: utf-8 -*-
{
    'name': 'Construction ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Construction',
    'summary': 'Projects, BOQ, site ops, procurement, labour, equipment, billing',
    'description': """
ARMORA Construction ERP Core for Odoo 19 Community
==================================================

Flagship vertical for contractors, builders, and infrastructure firms.

Phase 1 (rn_construction_core) delivers:

* Construction projects, sites, phases, milestones
* BOQ (Bill of Quantities) with revisions and cost roll-up
* Cost estimation: material, labour, equipment, overhead
* Site daily logs, progress, photos, incidents
* Material requests and procurement workflow hooks
* Site inventory consumption tracking
* Labour attendance and contractor records
* Equipment registry, utilization, maintenance
* Running bills, retention, milestone billing hooks
* Management, PM, and site engineer dashboards
* AI project assistant, cost risk, material forecast (heuristic)

Roadmap: mobile offline app, drawing search, subcontractor portal.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 249.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 68,
    'depends': [
        'base',
        'mail',
        'web',
        'account',
        'purchase',
        'stock',
        'hr',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/project_views.xml',
        'views/boq_views.xml',
        'views/site_views.xml',
        'views/procurement_views.xml',
        'views/labour_views.xml',
        'views/equipment_views.xml',
        'views/billing_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/material_request_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_construction_core/static/src/scss/construction_core.scss',
            'rn_construction_core/static/src/xml/construction_dashboard.xml',
            'rn_construction_core/static/src/xml/site_dashboard.xml',
            'rn_construction_core/static/src/js/construction_dashboard.js',
            'rn_construction_core/static/src/js/site_dashboard.js',
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

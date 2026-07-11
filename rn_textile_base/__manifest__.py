# -*- coding: utf-8 -*-
{
    'name': 'Textile Manufacturing Core',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/Textile',
    'summary': 'Factory master, departments, machines, yarn specs, and production dashboard',
    'description': """
ARMORA Textile Manufacturing Core for Odoo 19 Community
=======================================================

Vertical ERP foundation for spinning mills, knitting units, dyeing plants,
garment factories, export houses, and textile traders in Coimbatore, Tiruppur,
Erode, Karur, and beyond. One configurable codebase supports multiple unit types
through settings instead of hardcoded garment-only logic.

Phase 1 (rn_textile_base) delivers:

* Factory / plant master with unit type and compliance details
* Production departments and work centers
* Machine registry for knitting, dyeing, weaving, and utility assets
* Yarn specification master with count, blend, GSM, and lot traceability hooks
* Operations dashboard shell
* SaaS subscription tracking for hosted deployments

Companion modules (roadmap): CRM, yarn inventory, dyeing, knitting, weaving,
job work, MRP, quality, warehouse, export, purchase, accounts, HR, maintenance,
energy monitoring, and AI.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 57,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'calendar',
        'portal',
        'hr',
        'uom',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/cron.xml',
        'views/factory_views.xml',
        'views/department_views.xml',
        'views/machine_views.xml',
        'views/yarn_spec_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_textile_base/static/src/scss/textile.scss',
            'rn_textile_base/static/src/xml/textile_dashboard.xml',
            'rn_textile_base/static/src/js/textile_dashboard.js',
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

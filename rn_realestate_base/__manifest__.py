# -*- coding: utf-8 -*-
{
    'name': 'Real Estate ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Sales/Real Estate',
    'summary': 'Developer master, projects, property inventory, leads, and sales dashboard',
    'description': """
ARMORA Real Estate ERP Core for Odoo 19 Community
=================================================

Vertical ERP foundation for builders, property developers, villa promoters,
layout developers, and real estate agencies. Goes beyond generic CRM by
combining lead management with project hierarchy, unit inventory, and
Odoo-native hooks for booking, payments, and accounting companion modules.

Phase 1 (rn_realestate_base) delivers:

* Developer / builder master with RERA and compliance fields
* Projects with towers, blocks, floors, and unit inventory
* Unit status tracking (available, blocked, booked, sold)
* Lead management with source, budget, and sales stage
* Operations dashboard with pipeline and inventory KPIs
* SaaS subscription tracking for hosted deployments

Companion modules (roadmap): site visits, booking, payments, agreements,
commissions, construction progress, customer portal, accounting, reports, AI.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 58,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'calendar',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/cron.xml',
        'views/developer_views.xml',
        'views/project_views.xml',
        'views/block_views.xml',
        'views/unit_views.xml',
        'views/lead_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_realestate_base/static/src/scss/realestate.scss',
            'rn_realestate_base/static/src/xml/realestate_dashboard.xml',
            'rn_realestate_base/static/src/js/realestate_dashboard.js',
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

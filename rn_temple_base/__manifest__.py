# -*- coding: utf-8 -*-
{
    'name': 'Temple Management Core',
    'version': '19.0.1.0.0',
    'category': 'Services/Religion',
    'summary': 'Temple master, branches, trustees, priests, timings, and festival calendar',
    'description': """
ARMORA Temple Management Core for Odoo 19 Community
===================================================

Vertical ERP foundation for temples, trusts, ashrams, mutts, gurudwaras,
churches, and other religious institutions. One configurable codebase serves
multiple institution types through settings instead of hardcoded Hindu-only logic.

Phase 1 (rn_temple_base) delivers:

* Temple / institution master with trust and registration details
* Multi-branch management
* Trustees and priests
* Departments (ritual, kitchen, admin, security, etc.)
* Daily darshan and service timings
* Festival calendar with upcoming events
* Operations dashboard shell
* SaaS subscription tracking for hosted deployments

Companion modules (roadmap): devotee CRM, donations, seva booking, portal,
annadhanam, inventory, accounts, volunteers, HR, hall booking, queue, POS,
goshala, assets, reports, mobile API, and AI assistant.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 55,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'calendar',
        'portal',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/temple_data.xml',
        'data/cron.xml',
        'views/temple_views.xml',
        'views/branch_views.xml',
        'views/trustee_views.xml',
        'views/priest_views.xml',
        'views/department_views.xml',
        'views/timing_views.xml',
        'views/festival_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_temple_base/static/src/scss/temple.scss',
            'rn_temple_base/static/src/xml/temple_dashboard.xml',
            'rn_temple_base/static/src/js/temple_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

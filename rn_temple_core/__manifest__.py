# -*- coding: utf-8 -*-
{
    'name': 'Temple Digital Platform',
    'version': '19.0.1.0.0',
    'category': 'Religious Organizations',
    'summary': 'Devotees, donations, sevas, festivals, annadhanam, hundi, volunteers',
    'description': """
ARMORA Temple Digital Platform for Odoo 19 Community
====================================================

Modern cloud platform for temples, trusts, mutts, and religious organizations.

Phase 1 (rn_temple_core) delivers:

* Devotee profiles with family and donation history
* Donation management: cash, UPI, card, bank, cheque, online
* Seva catalog and booking with time slots and capacity
* Festival planning with sponsors and budgets
* Annadhanam: daily meals, sponsors, kitchen inventory hooks
* Hundi collection with audit trail
* Volunteer registration and event assignments
* Temple asset registry
* Trustee and office dashboards
* AI hooks: seva Q&A, donation analytics, event planning, receipt search

Roadmap: devotee mobile app, e-hundi, multi-language, hall booking, prasadam shop.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 69,
    'depends': [
        'base',
        'mail',
        'web',
        'website',
        'portal',
        'account',
        'hr',
        'stock',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/seva_type_data.xml',
        'views/devotee_views.xml',
        'views/donation_views.xml',
        'views/seva_views.xml',
        'views/festival_views.xml',
        'views/annadhanam_views.xml',
        'views/hundi_views.xml',
        'views/volunteer_views.xml',
        'views/asset_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/donation_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_temple_core/static/src/scss/temple_core.scss',
            'rn_temple_core/static/src/xml/trustee_dashboard.xml',
            'rn_temple_core/static/src/xml/office_dashboard.xml',
            'rn_temple_core/static/src/js/trustee_dashboard.js',
            'rn_temple_core/static/src/js/office_dashboard.js',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_temple_core_form.png',
        'static/description/screenshot_temple_core_list.png',
        'static/description/screenshot_temple_core_dashboard.png',
        'static/description/screenshot_temple_core_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

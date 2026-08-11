# -*- coding: utf-8 -*-
{
    'name': 'Rental Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/Rental',
    'summary': 'Assets, pricing, availability, and bookings for any rental business',
    'description': """
ARMORA Rental Core for Odoo 19 Community
========================================

Generic rental engine for cars, bikes, cameras, furniture, equipment,
and other rentable assets. Industry packs extend this core without
duplicating pricing or availability logic.

Phase 1 delivers assets, categories, pricing rules, availability engine,
lean bookings for reservation conflicts, OWL dashboard, settings, and
SaaS edition tracking. Companion modules handle payments, deposits,
returns, damage, website, and industry packs.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 48,
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
        'data/rental_data.xml',
        'data/cron.xml',
        'views/category_views.xml',
        'views/asset_views.xml',
        'views/pricing_views.xml',
        'views/booking_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/booking_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_rental_core/static/src/scss/rental.scss',
            'rn_rental_core/static/src/xml/rental_dashboard.xml',
            'rn_rental_core/static/src/js/rental_dashboard.js',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_rental_core_form.png',
        'static/description/screenshot_rental_core_list.png',
        'static/description/screenshot_rental_core_dashboard.png',
        'static/description/screenshot_rental_core_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

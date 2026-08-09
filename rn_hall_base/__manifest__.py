# -*- coding: utf-8 -*-
{
    'name': 'Marriage Hall Management Core',
    'version': '19.0.1.0.0',
    'category': 'Services/Events',
    'summary': 'Venue master, halls, capacity, booking calendar, and conflict detection',
    'description': """
ARMORA Marriage Hall Management Core for Odoo 19 Community
==========================================================

Vertical ERP foundation for marriage halls, convention centers, banquet halls,
community halls, and rentable event venues. One configurable codebase supports
multiple venue types through settings instead of hardcoded wedding-only logic.

Phase 1 (rn_hall_base) delivers:

* Venue / property master with registration and contact details
* Multiple halls with capacity, AC, parking, dining, kitchen, and stage flags
* Booking management with function types and muhurtham tracking
* Calendar views and conflict detection for double-booking prevention
* Tentative, waitlist, and confirmed booking workflow
* Operations dashboard shell
* SaaS subscription tracking for hosted deployments

Companion modules (roadmap): CRM, guest rooms, catering, decoration, vendors,
inventory, HR, payments, accounting, maintenance, portal, mobile API, and AI.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 56,
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
        'data/cron.xml',
        'views/venue_views.xml',
        'views/hall_views.xml',
        'views/booking_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hall_base/static/src/scss/hall.scss',
            'rn_hall_base/static/src/xml/hall_dashboard.xml',
            'rn_hall_base/static/src/js/hall_dashboard.js',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_hall_base_form.png',
        'static/description/screenshot_hall_base_list.png',
        'static/description/screenshot_hall_base_dashboard.png',
        'static/description/screenshot_hall_base_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

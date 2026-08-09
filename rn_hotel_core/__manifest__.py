# -*- coding: utf-8 -*-
{
    'name': 'Hotel ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Hospitality',
    'summary': 'Reservations, front desk, housekeeping, folio billing for boutique hotels',
    'description': """
ARMORA Hotel ERP Core for Odoo 19 Community
============================================

Boutique hotels, resorts, homestay chains, and serviced apartments on Odoo.

Phase 1 (rn_hotel_core) delivers:

* Room types and rooms with live status board
* Reservations: walk-in, online-ready, group hooks
* Front desk check-in and check-out with guest folio
* Housekeeping workflow: dirty, cleaning, inspection, available
* Guest profiles and stay history
* Folio charges linked to accounting invoices
* Room service order foundation
* Maintenance request tracking
* GM, reception, and housekeeping dashboards
* AI hooks: revenue insights, pricing suggestions, concierge replies

Roadmap: OTA channel manager, POS restaurant, door locks, guest mobile portal.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 64,
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
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/room_type_data.xml',
        'views/room_views.xml',
        'views/guest_views.xml',
        'views/reservation_views.xml',
        'views/folio_views.xml',
        'views/housekeeping_views.xml',
        'views/maintenance_views.xml',
        'views/room_service_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/checkin_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hotel_core/static/src/scss/hotel_core.scss',
            'rn_hotel_core/static/src/xml/hotel_dashboard.xml',
            'rn_hotel_core/static/src/xml/room_board.xml',
            'rn_hotel_core/static/src/js/hotel_dashboard.js',
            'rn_hotel_core/static/src/js/room_board.js',
        ],
    },
                    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_hotel_core_form.png',
        'static/description/screenshot_hotel_core_list.png',
        'static/description/screenshot_hotel_core_dashboard.png',
        'static/description/screenshot_hotel_core_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

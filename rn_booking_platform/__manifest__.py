# -*- coding: utf-8 -*-
{
    'name': 'Appointment Booking',
    'version': '19.0.1.0.0',
    'category': 'Services/Appointment',
    'summary': 'Online booking, resources, and calendar sync',
    'description': """
ARMORA Appointment Booking Pro for Odoo 19 Community
====================================================

Universal appointment and scheduling platform for clinics, salons,
consultants, service businesses, and multi-branch organizations.

Phase 1 delivers the installable core: industries, services, staff,
locations, resources, appointments, working hours, availability engine
hooks, OWL dashboard shell, security, menus, and docs.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 45,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'calendar',
        'portal',
        'website',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/industry_data.xml',
        'data/cron.xml',
        'views/industry_views.xml',
        'views/location_views.xml',
        'views/service_views.xml',
        'views/staff_views.xml',
        'views/resource_views.xml',
        'views/appointment_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/appointment_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_booking_platform/static/src/scss/booking.scss',
            'rn_booking_platform/static/src/xml/booking_dashboard.xml',
            'rn_booking_platform/static/src/js/booking_dashboard.js',
        ],
    },
            'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_form.png',
        'static/description/screenshot_list.png',
        'static/description/screenshot_dashboard.png',
        'static/description/screenshot_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

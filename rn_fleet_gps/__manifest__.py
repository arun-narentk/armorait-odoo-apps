# -*- coding: utf-8 -*-
{
    'name': 'Fleet GPS Tracking',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Fleet',
    'summary': 'Live tracking, trips, geofences, and fleet alerts',
    'description': """
ARMORA Fleet GPS for Odoo 19 Community
======================================

Extends standard Fleet with a provider-agnostic GPS layer.

Phase 1 delivers GPS devices, live location ingestion, trips,
driver assignment, fuel and expense logs, geofences, alerts,
OWL fleet dashboard, REST API stubs, and a connector framework
for Traccar / Teltonika / GT06 / Wialon / Ruptela / TK103 add-ons.

Integrates with Fleet without requiring Enterprise features.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 47,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'fleet',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/fleet_data.xml',
        'data/cron.xml',
        'views/device_views.xml',
        'views/location_views.xml',
        'views/trip_views.xml',
        'views/geofence_views.xml',
        'views/alert_views.xml',
        'views/fuel_views.xml',
        'views/expense_views.xml',
        'views/driver_views.xml',
        'views/vehicle_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/fleet_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_fleet_gps/static/src/scss/fleet_gps.scss',
            'rn_fleet_gps/static/src/xml/fleet_dashboard.xml',
            'rn_fleet_gps/static/src/js/fleet_dashboard.js',
        ],
    },
        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/dashboard.png',
        'static/description/overview.png',
        'static/description/form.png',
        'static/description/list.png',
        'static/description/kanban.png',
        'static/description/wizard.png',
        'static/description/designer.png',
        'static/description/search.png',
        'static/description/settings.png',
        'static/description/report.png',
        'static/description/workflow.png',
        'static/description/mobile.png',
        'static/description/hero.gif',
        'static/description/dashboard.gif',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

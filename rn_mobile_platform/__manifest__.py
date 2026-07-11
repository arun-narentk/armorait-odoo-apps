# -*- coding: utf-8 -*-
{
    'name': 'Mobile Platform',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Metadata-driven mobile experience platform for Odoo apps, offline sync, device features, and branded deployments',
    'description': """
Mobile Platform for Odoo 19 Community
=====================================

Not just a mobile app builder. A metadata-driven mobile experience platform for
Odoo that defines business apps through screens, sync rules, device features,
branding, and reusable mobile engines.

Phase 1 delivers:

* Mobile app definitions for warehouse, sales, service, customer, and manager use cases
* Screen metadata for list, form, dashboard, cards, barcode, camera, map, and signature flows
* Offline sync profiles with model-level caching and sync priority rules
* Device feature toggles for barcode, camera, GPS, push, and signature support
* Branded theme settings for white-label mobile rollouts
* Executive dashboard for app adoption, sync posture, and feature usage
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 52,
    'depends': [
        'base',
        'mail',
        'web',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/app_data.xml',
        'views/app_views.xml',
        'views/screen_views.xml',
        'views/sync_views.xml',
        'views/theme_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_mobile_platform/static/src/scss/mobile_platform.scss',
            'rn_mobile_platform/static/src/xml/mobile_platform_dashboard.xml',
            'rn_mobile_platform/static/src/js/mobile_platform_dashboard.js',
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

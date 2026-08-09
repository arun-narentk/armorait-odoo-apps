# -*- coding: utf-8 -*-
{
    'name': 'Customer Experience Portal',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Customer self-service experience portal: orders, invoices, payments, downloads, and widgets',
    'description': """
Customer Self-Service Experience Platform for Odoo 19
=====================================================

Not just a customer portal. A branded experience platform that reduces support calls,
speeds payments, and improves retention.

Phase 1: modern mobile-first dashboard, orders, invoices, payments, downloads,
widget-based page builder foundation, and analytics.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 79.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 47,
    'depends': [
        'base',
        'mail',
        'web',
        'portal',
        'website',
        'sale',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/widget_data.xml',
        'data/page_data.xml',
        'views/config_views.xml',
        'views/widget_views.xml',
        'views/ticket_views.xml',
        'views/warranty_views.xml',
        'views/amc_views.xml',
        'views/analytics_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'views/portal_templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rn_customer_experience/static/src/scss/portal_experience.scss',
            'rn_customer_experience/static/src/js/portal_experience.js',
        ],
        'web.assets_backend': [
            'rn_customer_experience/static/src/scss/backend_experience.scss',
            'rn_customer_experience/static/src/xml/experience_dashboard.xml',
            'rn_customer_experience/static/src/js/experience_dashboard.js',
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

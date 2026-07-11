# -*- coding: utf-8 -*-
{
    'name': 'Record Share',
    'version': '19.0.1.1.0',
    'category': 'Productivity',
    'summary': 'Share Odoo records with secure links, copy formats, QR bridge, and share history',
    'description': """
Record Share for Odoo 19 Community
==================================

Instantly share any Odoo record with secure links, multiple copy formats,
email and WhatsApp helpers, optional QR integration, and share history.

Features
--------

* Copy Link on sale orders, contacts, CRM leads, invoices, products, projects, and tasks
* Keyboard shortcut Ctrl+Shift+C on any supported form view
* Share wizard with URL, Markdown, HTML, JSON, and record name formats
* Permission checks before any link is exposed
* Share history and analytics per user
* Optional bridge to Universal QR Generator when installed
* Configurable default format and log retention
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 54,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
        'account',
        'crm',
        'contacts',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/share_log_views.xml',
        'views/settings_views.xml',
        'wizard/record_share_wizard_views.xml',
        'views/inherited_form_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_record_share/static/src/js/record_share_clipboard.js',
            'rn_record_share/static/src/js/record_share_hotkey.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/workflow.png',
        'static/description/dashboard.png',
        'static/description/designer.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

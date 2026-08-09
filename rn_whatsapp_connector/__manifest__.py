# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Automation',
    'version': '19.0.1.0.0',
    'category': 'Marketing/WhatsApp',
    'summary': 'Send invoices, orders, and alerts on WhatsApp from Odoo 19',
    'description': """
ARMORA WhatsApp Automation Platform for Odoo 19 Community
=======================================================

Complete communication automation on WhatsApp. Not just an API connector.

Phase 1 delivers:
- Multi-provider account layer (Meta Cloud, Twilio, 360Dialog, Gupshup, Interakt)
- Message templates with variables
- Message queue with retries and scheduling
- Message log / history and webhook intake
- Generic automation engine (registerable triggers)
- Sales / Invoice / Delivery helper hooks
- OWL KPI dashboard
- Multi-company security and SaaS edition tracking

Higher editions add team inbox, campaigns, REST API, and high-volume tooling.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 79.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 45,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'crm',
        'sale_management',
        'purchase',
        'account',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/message_templates.xml',
        'data/automation_data.xml',
        'data/cron.xml',
        'data/ir_config_parameter.xml',
        'views/account_views.xml',
        'views/template_views.xml',
        'views/message_views.xml',
        'views/queue_views.xml',
        'views/automation_views.xml',
        'views/history_views.xml',
        'views/wizard_views.xml',
        'views/dashboard_views.xml',
        'views/settings_views.xml',
        'views/menu.xml',
        'report/message_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_whatsapp_connector/static/src/scss/whatsapp_connector.scss',
            'rn_whatsapp_connector/static/src/xml/whatsapp_dashboard.xml',
            'rn_whatsapp_connector/static/src/js/whatsapp_dashboard.js',
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

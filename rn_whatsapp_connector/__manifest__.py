# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Connector',
    'version': '19.0.1.0.0',
    'category': 'Marketing/WhatsApp',
    'summary': 'Multi-provider WhatsApp messaging for CRM, Sales, Accounting, and more',
    'description': """
WhatsApp Connector for Odoo 19 Community
======================================

Commercial-grade WhatsApp integration with provider abstraction, templates,
webhooks, automation, and OWL chat (upcoming phases).

Phase 1 delivers the module skeleton: security, menus, configuration, and
extensible service architecture.
    """,
    'author': 'ARMORAIT',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'LGPL-3',
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
        'data/cron.xml',
        'data/ir_config_parameter.xml',
        'data/ir_config_parameter.xml',
        'views/menu.xml',
        'views/settings_views.xml',
        'views/account_views.xml',
        'views/message_views.xml',
        'views/template_views.xml',
        'views/history_views.xml',
        'views/wizard_views.xml',
        'views/dashboard_views.xml',
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
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

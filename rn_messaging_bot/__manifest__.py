# -*- coding: utf-8 -*-
{
    'name': 'Messaging Bot Engine',
    'version': '19.0.2.0.0',
    'category': 'Marketing',
    'summary': 'Omnichannel messaging connectors with visual bot flows for WhatsApp, Facebook, and Instagram',
    'description': """
Messaging Bot Engine for Odoo 19
================================

Unified inbox and bot engine for customer messaging channels.

Includes connector registry, conversation inbox, visual bot flow designer,
WhatsApp / Facebook / Instagram drivers, outbound queue with retries,
agent reply composer, and optional bridge to rn_whatsapp_connector.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 79.99,
    'live_test_url': 'https://www.armorait.com',
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'crm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'data/bot_demo_flow.xml',
        'views/rn_messaging_connector_views.xml',
        'views/rn_messaging_conversation_views.xml',
        'views/rn_messaging_bot_views.xml',
        'views/rn_messaging_queue_views.xml',
        'views/rn_messaging_menus.xml',
        'wizard/compose_reply_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_messaging_bot/static/src/scss/messaging_bot.scss',
            'rn_messaging_bot/static/src/xml/bot_flow_designer.xml',
            'rn_messaging_bot/static/src/js/bot_flow_designer.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'Conversational ERP',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Natural conversation interface for ERP actions, approvals, and AI-assisted workflows',
    'description': """
Conversational ERP for Odoo 19 Community
=======================================

Not just WhatsApp ERP. A channel-agnostic conversation layer for ERP actions,
approvals, employee requests, executive queries, and domain assistants.

Phase 1 delivers:

* Channel accounts for WhatsApp, Teams, Slack, Telegram, voice, SMS, email, and app
* Domain assistants for employee, customer, executive, sales, finance, and inventory flows
* Conversation inbox with routed intent classification
* Approval center records with approve and reject actions
* Executive operations dashboard with channel and approval visibility
* Human-review-first architecture for sensitive ERP actions
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 49,
    'depends': [
        'base',
        'mail',
        'web',
        'hr_holidays',
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/assistant_data.xml',
        'views/channel_views.xml',
        'views/assistant_views.xml',
        'views/conversation_views.xml',
        'views/approval_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_conversational_erp/static/src/scss/conversational_erp.scss',
            'rn_conversational_erp/static/src/xml/conversational_dashboard.xml',
            'rn_conversational_erp/static/src/js/conversational_dashboard.js',
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

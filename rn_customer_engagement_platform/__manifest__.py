# -*- coding: utf-8 -*-
{
    'name': 'Customer Engagement Platform',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'AI customer engagement across web, messaging, email, and voice with Odoo-aware self service',
    'description': """
Customer Engagement Platform for Odoo 19 Community
==================================================

Not just an AI chatbot connected to Odoo. A customer engagement platform that
combines customer authentication, Odoo record access, company knowledge, self-service
workflows, and escalation across multiple channels.

Phase 1 delivers:

* Customer channels for website, WhatsApp, Telegram, email, voice, and mobile
* Customer authentication sessions with OTP-ready strategy fields
* Knowledge articles linked to support, policy, and product answers
* AI-style conversation routing for orders, invoices, payments, deliveries, and support
* Escalation to tickets when the assistant should hand off to a human
* Executive dashboard for channel activity, sessions, escalations, and knowledge usage
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 50,
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
        'data/channel_data.xml',
        'data/knowledge_data.xml',
        'views/channel_views.xml',
        'views/session_views.xml',
        'views/knowledge_views.xml',
        'views/conversation_views.xml',
        'views/escalation_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_customer_engagement_platform/static/src/scss/customer_engagement.scss',
            'rn_customer_engagement_platform/static/src/xml/customer_engagement_dashboard.xml',
            'rn_customer_engagement_platform/static/src/js/customer_engagement_dashboard.js',
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

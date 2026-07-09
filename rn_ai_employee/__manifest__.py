# -*- coding: utf-8 -*-
{
    'name': 'AI Employee',
    'version': '19.0.3.1.0',
    'category': 'Productivity',
    'summary': 'AI assistant for Odoo: analytics, LLM routing, quotations, reminders, systray chat',
    'description': """
AI Employee for Odoo 19
=======================

Ask everyday business questions in plain language and get answers from live Odoo data.

**Key points**
* 20+ analytics and action tools across Sales, Accounting, Inventory, and CRM
* OpenAI-compatible LLM routing with rules fallback
* Backend systray chat widget
* Guided write tools: create quotation, send payment reminders
* Action cards: Open List, Open Record, Create Activity
* Permission-aware ORM tools
* Community, Enterprise, and Odoo.sh compatible

**Self-service**
Install, enable, and use it in your own Odoo environment.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'currency': 'USD',
    'depends': [
        'base',
        'web',
        'mail',
        'sale_management',
        'stock',
        'account',
        'crm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/rn_ai_employee_tool_data.xml',
        'data/rn_ai_employee_suggestion_data.xml',
        'views/rn_ai_employee_chat_views.xml',
        'views/rn_ai_employee_tool_views.xml',
        'views/rn_ai_employee_suggestion_views.xml',
        'views/res_config_settings_views.xml',
        'views/rn_ai_employee_menus.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/overview.png',
        'static/description/settings.png',
        'static/description/tools.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'rn_ai_employee/static/src/scss/ai_employee_systray.scss',
            'rn_ai_employee/static/src/xml/ai_employee_systray.xml',
            'rn_ai_employee/static/src/js/ai_employee_systray.js',
        ],
    },
}

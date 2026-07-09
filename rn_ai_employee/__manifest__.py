# -*- coding: utf-8 -*-
{
    'name': 'AI Chatbot',
    'version': '19.0.2.13.0',
    'category': 'Productivity',
    'summary': 'Ask Odoo anything. Get answers and actions from an AI copilot',
    'description': """
AI Copilot for Odoo 19
======================

Ask everyday business questions in plain language and get answers from live Odoo data.

**Key points**
* Suggested questions for managers
* Analytics across Sales, Accounting, Inventory, and CRM
* Action cards: Open List and Create Activity
* Permission-aware ORM tools
* Community, Enterprise, and Odoo.sh compatible

**Self-service**
Install, enable, and use it in your own Odoo environment.

Phase 1 focuses on analytics (read-only). Guided write actions arrive later.
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
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'AI Copilot for Odoo',
    'version': '19.0.2.3.0',
    'category': 'Productivity',
    'summary': 'Business assistant for sales, accounting, inventory, and CRM insights',
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
    'author': 'ARMORAIT',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'LGPL-3',
    'price': 49.0,
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
        'data/ai_employee_tool_data.xml',
        'data/ai_employee_suggestion_data.xml',
        'views/ai_employee_chat_views.xml',
        'views/ai_employee_tool_views.xml',
        'views/ai_employee_suggestion_views.xml',
        'views/res_config_settings_views.xml',
        'views/ai_employee_menus.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
        'static/description/icon.png',
        'static/description/screenshot_repository_register.png',
        'static/description/screenshot_repository_scan.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

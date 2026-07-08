# -*- coding: utf-8 -*-
{
    'name': 'AI Copilot for Odoo',
    'version': '19.0.2.1.1',
    'category': 'Productivity',
    'summary': 'Business assistant for sales, accounting, inventory, and CRM insights',
    'description': """
AI Copilot for Odoo 19 Community
================================

Ask everyday business questions and get useful answers in minutes.

**Sales**
* Show today's sales
* Show pending quotations
* Top customers and best selling products

**Accounting**
* Overdue invoices
* Revenue, expenses, and profit this month
* Why revenue changed

**Inventory**
* Low stock and negative stock
* Products not moved
* Inventory valuation

**CRM**
* Top opportunities and pipeline revenue
* Overdue follow-ups

Phase 1 focuses on analytics (read-only). Guided write actions arrive in Phase 2.
    """,
    'author': 'ARMORAIT',
    'website': 'https://www.armorait.com',
    'license': 'LGPL-3',
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
        'static/description/screenshot_actions.png',
        'static/description/screenshot_settings.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'AI Chatbot',
    'version': '19.0.4.0.0',
    'category': 'Productivity',
    'summary': 'Ask Odoo anything. Get answers and actions from an AI copilot',
    'description': """
AI Copilot for Odoo 19
======================

The intelligence layer for your Odoo ERP. Ask business questions, run guided
write skills, and get proactive executive briefings from live company data.

**Platform capabilities**
* 25+ analytics and write skills across Sales, Finance, Inventory, CRM, and Purchase
* Session memory for follow-up questions ("email the first three customers")
* Confirmation gates and audit logs for every write action
* OpenAI-compatible LLM routing with rules fallback
* Backend systray copilot widget
* Proactive morning briefing cron for managers
* Permission-aware ORM skills

**Self-service**
Install, enable, and use it in your own Odoo environment.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'price': 99.99,
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
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/rn_ai_employee_tool_data.xml',
        'data/rn_ai_employee_suggestion_data.xml',
        'data/rn_ai_employee_cron.xml',
        'views/rn_ai_employee_chat_views.xml',
        'views/rn_ai_employee_tool_views.xml',
        'views/rn_ai_employee_suggestion_views.xml',
        'views/rn_ai_employee_audit_log_views.xml',
        'views/res_config_settings_views.xml',
        'views/rn_ai_employee_menus.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/overview.png',
        'static/description/dashboard.png',
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

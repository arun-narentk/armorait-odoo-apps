# -*- coding: utf-8 -*-
{
    'name': 'AI Email Intelligence',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Context-aware AI email drafts for CRM, sales, accounting, and HR',
    'description': """
ARMORA AI Email Intelligence for Odoo 19 Community
==================================================

Generate emails using real Odoo business context, not generic prompts.

Phase 1 (rn_ai_email_intelligence) delivers:

* Smart context from partner, sales orders, invoices, activities
* AI email drafts with tone selection (professional, friendly, formal, etc.)
* Category templates: sales follow-up, payment reminder, CRM outreach, HR
* Compose wizard from partner, quotation, invoice, and lead records
* Multilingual draft hooks (English, Tamil, Hindi, and more)
* Draft review, edit, and send via mail.thread
* Usage credits and SaaS-ready settings
* OWL dashboard: drafts generated, tones, categories

Roadmap: reply suggestions, sentiment analysis, campaigns, attachment
intelligence, AI copilot commands, Gmail/Outlook sync.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 46,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'crm',
        'sale',
        'account',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/email_template_data.xml',
        'views/template_views.xml',
        'views/draft_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/compose_email_wizard_views.xml',
        'views/integration_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_ai_email_intelligence/static/src/scss/ai_email.scss',
            'rn_ai_email_intelligence/static/src/xml/email_dashboard.xml',
            'rn_ai_email_intelligence/static/src/js/email_dashboard.js',
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

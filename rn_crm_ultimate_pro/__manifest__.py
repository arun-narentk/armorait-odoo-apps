# -*- coding: utf-8 -*-
{
    'name': 'CRM Ultimate Pro',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Lead scoring, duplicates, follow-ups, forecasting, and CRM dashboard for Odoo 19',
    'description': """
CRM Ultimate Pro for Odoo 19 Community
======================================

Commercial CRM enhancement suite: scoring, prediction hooks, duplicate
detection, merge, follow-up automation, and OWL dashboard.

Phase 1 delivers the installable skeleton, security, menus, models,
and service stubs. Feature engines arrive in later phases.
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
        'calendar',
        'crm',
        'sale_management',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/lead_score_rules.xml',
        'data/cron.xml',
        'data/email_templates.xml',
        'data/ir_config_parameter.xml',
        'views/score_views.xml',
        'views/duplicate_views.xml',
        'views/activity_views.xml',
        'views/crm_views.xml',
        'views/dashboard.xml',
        'views/settings.xml',
        'views/wizard_views.xml',
        'views/menu.xml',
        'report/crm_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_crm_ultimate_pro/static/src/scss/crm_ultimate.scss',
            'rn_crm_ultimate_pro/static/src/xml/crm_dashboard.xml',
            'rn_crm_ultimate_pro/static/src/js/crm_dashboard.js',
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

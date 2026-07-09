# -*- coding: utf-8 -*-
{
    'name': 'AI Document Automation',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Templates, AI drafts, approvals, and PDF output',
    'description': """
ARMORA AI Document Automation for Odoo 19 Community
===================================================

Foundation of the ARMORA Document Automation Platform.

Phase 1 delivers document types, HTML templates with placeholders,
AI content generation (pluggable provider + built-in drafts),
document records with preview, approval workflow stubs,
version history, PDF render hooks, OWL dashboard, and
multi-company security.

Companion modules can later add advanced e-sign, contract review,
template marketplace, and bulk generation.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 59.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 42,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/document_data.xml',
        'data/cron.xml',
        'views/document_type_views.xml',
        'views/template_views.xml',
        'views/document_views.xml',
        'views/version_views.xml',
        'views/approval_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/document_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_ai_document_generator/static/src/scss/document.scss',
            'rn_ai_document_generator/static/src/xml/document_dashboard.xml',
            'rn_ai_document_generator/static/src/js/document_dashboard.js',
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

# -*- coding: utf-8 -*-
{
    'name': 'AI Document Processing',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Documents',
    'summary': 'AI Intelligent Document Processing: capture, classify, extract, validate, and post to Odoo',
    'description': """
AI Intelligent Document Processing (IDP) for Odoo 19
==================================================

Document gateway for your ERP. Not just OCR.

Pipeline: Capture > Classify > Extract > Validate > Business Rules > Review > Odoo Transaction

Phase 1 delivers vendor invoices, purchase orders, delivery challans, review queue,
confidence scoring, duplicate detection, three-way match hooks, and analytics dashboard.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 55,
    'depends': [
        'base',
        'mail',
        'web',
        'account',
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/document_type_data.xml',
        'views/document_views.xml',
        'views/validation_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/post_document_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_document_idp/static/src/scss/document_idp.scss',
            'rn_document_idp/static/src/xml/document_idp_dashboard.xml',
            'rn_document_idp/static/src/js/document_idp_dashboard.js',
        ],
    },
                    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_document_idp_form.png',
        'static/description/screenshot_document_idp_list.png',
        'static/description/screenshot_document_idp_dashboard.png',
        'static/description/screenshot_document_idp_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'Digital Document Platform',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Documents',
    'summary': 'Sign, approve, audit, and AI-analyze contracts and business documents',
    'description': """
ARMORA Digital Document Platform for Odoo 19 Community
======================================================

Enterprise document workflow beyond basic e-sign: approval, signing, audit,
delivery, and AI contract intelligence.

Phase 1 (rn_document_platform) delivers:

* Sign requests linked to any Odoo document (sales, purchase, HR, accounting)
* Multi-signer sequential and parallel flows
* PDF attachment with signature field placement
* Email invitations and reminder hooks
* Full audit trail (IP, user agent, timestamp, document hash)
* Built-in signature capture and completion tracking
* AI contract summary and risk flag hooks (heuristic Phase 1)
* OWL dashboard: pending, expiring, completion rate
* SaaS signature credit tracking

Roadmap: Aadhaar eSign, DSC/USB token, AI clause detection, document
comparison, WhatsApp delivery, public signing portal, rn_approval_engine
integration, mobile signing.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 48,
    'depends': [
        'base',
        'mail',
        'web',
        'portal',
        'website',
        'contacts',
        'sale',
        'purchase',
        'hr',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'views/template_views.xml',
        'views/sign_request_views.xml',
        'views/audit_views.xml',
        'views/analysis_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/send_signature_wizard_views.xml',
        'views/portal_templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_document_platform/static/src/scss/document_platform.scss',
            'rn_document_platform/static/src/xml/document_dashboard.xml',
            'rn_document_platform/static/src/js/document_dashboard.js',
        ],
    },
                    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_document_platform_form.png',
        'static/description/screenshot_document_platform_list.png',
        'static/description/screenshot_document_platform_dashboard.png',
        'static/description/screenshot_document_platform_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

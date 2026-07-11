# -*- coding: utf-8 -*-
{
    'name': 'AI Invoice OCR',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Upload supplier invoices, OCR extract fields, match vendor, create vendor bill',
    'description': """
ARMORA AI Invoice OCR for Odoo 19 Community
===========================================

Turn supplier invoice PDFs and images into draft vendor bills with review.

Phase 1 (rn_ai_invoice_ocr) delivers:

* Drag-and-drop upload (PDF, JPG, PNG, multi-page PDF)
* Text extraction and field parsing (vendor, GSTIN, invoice no, dates, amounts)
* Line item extraction with confidence scores
* India GST recognition (CGST, SGST, IGST, HSN hooks)
* Fuzzy vendor and product matching
* Duplicate invoice detection
* One-click draft vendor bill creation
* Purchase order link field for 3-way match hooks
* AI credit tracking and SaaS subscription model

Companion modules (roadmap): LLM document AI, PO matching, fraud detection,
account suggestions, email intake, learning engine.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 60,
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
        'views/scan_views.xml',
        'views/mapping_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/create_bill_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_ai_invoice_ocr/static/src/scss/invoice_ocr.scss',
            'rn_ai_invoice_ocr/static/src/xml/invoice_ocr_dashboard.xml',
            'rn_ai_invoice_ocr/static/src/js/invoice_ocr_dashboard.js',
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

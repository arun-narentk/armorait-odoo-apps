# -*- coding: utf-8 -*-
{
    'name': 'Invoice Duplicate Number Warning',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Prevent duplicate vendor invoices by detecting reused bill numbers before posting',
    'description': """
Prevent Duplicate Vendor Invoices
=================================

Detects when a vendor bill reuses the same invoice number (Bill Reference)
for the same vendor and company, then warns or blocks posting.

* Warning mode (default): confirm before posting
* Block mode: prevent posting until the reference is unique
* Case-insensitive and trimmed reference matching
* Multi-company safe
* Commercial partner aware
* Vendor bills only (customer invoices and credit notes are out of scope)
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'LGPL-3',
    'currency': 'USD',
    'price': 5.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 52,
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'wizard/duplicate_invoice_warning_wizard_views.xml',
    ],
    'demo': [],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

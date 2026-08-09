# -*- coding: utf-8 -*-
{
    'name': 'Smart Duplicate Finder',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Find and merge duplicate records on any Odoo model using fuzzy matching rules',
    'description': """
ARMORA Smart Duplicate Finder for Odoo 19 Community
===================================================

Generic duplicate detection framework for any Odoo model.

* Configurable rules per model (contacts, products, employees, custom models)
* Weighted field matching with exact, fuzzy, and phone modes
* Duplicate scan batches with similarity scoring
* Ignore pairs to suppress false positives
* Merge wizard with native partner merge support
* Scheduled automatic scans
* Multi-company aware
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 29.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 55,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'product',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/cron.xml',
        'data/duplicate_rule_data.xml',
        'views/duplicate_rule_views.xml',
        'views/duplicate_scan_views.xml',
        'views/duplicate_result_views.xml',
        'views/duplicate_ignore_views.xml',
        'views/menu.xml',
        'wizard/duplicate_merge_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
            'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_form.png',
        'static/description/screenshot_list.png',
        'static/description/screenshot_dashboard.png',
        'static/description/screenshot_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'Field Difference Viewer',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Visual before/after field change log with highlights, summaries, and history viewer',
    'description': """
ARMORA Field Difference Viewer for Odoo 19 Community
====================================================

Transform Odoo chatter tracking into readable change logs.

* Structured before/after comparisons on tracked fields
* Numeric, date, boolean, selection, and relational diffs
* History smart button with timeline and filters
* Color-coded added, removed, and modified values
* CSV and PDF export for audit teams
* Built on standard mail.tracking.value data
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 57,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
        'account',
        'crm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/field_diff_views.xml',
        'views/inherited_form_views.xml',
        'views/menu.xml',
        'wizard/diff_export_wizard_views.xml',
        'report/field_diff_report.xml',
        'report/field_diff_report_templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_field_diff/static/src/field_diff.scss',
            'rn_field_diff/static/src/field_diff_service.js',
            'rn_field_diff/static/src/diff_viewer_dialog.js',
            'rn_field_diff/static/src/diff_viewer_dialog.xml',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_field_diff_form.png',
        'static/description/screenshot_field_diff_list.png',
        'static/description/screenshot_field_diff_dashboard.png',
        'static/description/screenshot_field_diff_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

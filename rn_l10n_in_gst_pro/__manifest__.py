# -*- coding: utf-8 -*-
{
    'name': 'GST Reports',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'GSTR-1, GSTR-3B, GSTR-9, and GST validation for India',
    'description': """
India GST Compliance Pro for Odoo 19 Community
==============================================

Production-oriented GST compliance layer on top of l10n_in.

Phase 1 delivers the installable skeleton: security, menus, masters,
return shell models, service stubs, OWL dashboard placeholder, and tests.

Later phases add GSTR computation, JSON/Excel/PDF export, reconciliation,
and GSTN workflow features.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 39,
    'countries': ['IN'],
    'depends': [
        'base',
        'mail',
        'contacts',
        'account',
        'sale',
        'purchase',
        'stock',
        'l10n_in',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/gst_return_period.xml',
        'data/cron.xml',
        'data/ir_config_parameter.xml',
        'views/gst_period_views.xml',
        'views/gst_return_views.xml',
        'views/gst_summary_views.xml',
        'views/gst_validation_views.xml',
        'views/gst_settings_views.xml',
        'views/gst_dashboard.xml',
        'views/wizard_views.xml',
        'views/menu.xml',
        'report/gst_pdf.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_l10n_in_gst_pro/static/src/scss/gst_pro.scss',
            'rn_l10n_in_gst_pro/static/src/xml/gst_dashboard.xml',
            'rn_l10n_in_gst_pro/static/src/js/gst_dashboard.js',
        ],
    },
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

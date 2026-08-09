# -*- coding: utf-8 -*-
{
    'name': 'Filter Manager',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Organize, share, pin, and manage Odoo filters with folders, favorites, recent history, and team sharing',
    'description': """
Filter Manager for Odoo 19 Community
====================================

Turn Odoo favorites into a first-class navigation tool with folders, pinning,
team sharing, usage analytics, and JSON import/export.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 53,
    'depends': ['base', 'mail', 'web', 'sale', 'account', 'crm', 'contacts', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/filter_folder_views.xml',
        'views/filter_views.xml',
        'views/filter_history_views.xml',
        'views/settings_views.xml',
        'wizard/filter_import_export_wizard_views.xml',
        'views/menu.xml',
    ],
    'demo': ['demo/demo.xml'],
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_filter_manager_form.png',
        'static/description/screenshot_filter_manager_list.png',
        'static/description/screenshot_filter_manager_dashboard.png',
        'static/description/screenshot_filter_manager_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

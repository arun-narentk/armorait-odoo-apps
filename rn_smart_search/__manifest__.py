# -*- coding: utf-8 -*-
{
    'name': 'Smart Search',
    'version': '19.0.1.0.1',
    'category': 'Productivity',
    'summary': 'Recent records, search history, favorites, and Ctrl+K quick reopen',
    'description': """
ARMORA Smart Search for Odoo 19 Community
=========================================

Jump back to recent records and searches without digging through menus.

Features
--------

* Automatic view tracking on sale orders, contacts, CRM leads, invoices, and products
* Search query history for the command palette
* Favorites and a dedicated Smart Search workspace
* Systray shortcut and Ctrl+K provider for quick reopen
* Configurable retention, max history, and daily cleanup cron
* Per-user security with Odoo 19 privilege groups
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 7.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 49,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
        'account',
        'crm',
        'contacts',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/search_history_views.xml',
        'views/settings_views.xml',
        'views/inherited_form_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_smart_search/static/src/smart_search_tracker.xml',
            'rn_smart_search/static/src/smart_search_tracker.js',
            'rn_smart_search/static/src/smart_search_workspace.scss',
            'rn_smart_search/static/src/smart_search_workspace.xml',
            'rn_smart_search/static/src/smart_search_workspace.js',
            'rn_smart_search/static/src/smart_search_commands.js',
            'rn_smart_search/static/src/smart_search_systray.scss',
            'rn_smart_search/static/src/smart_search_systray.xml',
            'rn_smart_search/static/src/smart_search_systray.js',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_smart_search_form.png',
        'static/description/screenshot_smart_search_list.png',
        'static/description/screenshot_smart_search_dashboard.png',
        'static/description/screenshot_smart_search_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

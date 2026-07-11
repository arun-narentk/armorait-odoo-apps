# -*- coding: utf-8 -*-
{
    'name': 'Bookmarks',
    'version': '19.0.1.1.0',
    'category': 'Productivity',
    'summary': 'Bookmark any Odoo record, list view, menu, or report and open it instantly from a sidebar',
    'description': """
Bookmarks for Odoo 19 Community
=================================
Universal bookmarking with folders, pins, colors, notes, tags, and quick navigation.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 54,
    'depends': ['base', 'mail', 'web', 'sale', 'purchase', 'account', 'crm', 'contacts', 'product', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/bookmark_folder_views.xml',
        'views/bookmark_tag_views.xml',
        'views/bookmark_views.xml',
        'views/settings_views.xml',
        'views/inherited_form_views.xml',
        'wizard/bookmark_create_wizard_views.xml',
        'views/menu.xml',
    ],
    'demo': ['demo/demo.xml'],
    'assets': {
        'web.assets_backend': [
            'rn_bookmarks/static/src/bookmarks_systray.js',
            'rn_bookmarks/static/src/bookmarks_sidebar.scss',
            'rn_bookmarks/static/src/bookmark_toggle.xml',
            'rn_bookmarks/static/src/bookmark_toggle.js',
            'rn_bookmarks/static/src/bookmarks_sidebar.xml',
            'rn_bookmarks/static/src/bookmarks_sidebar.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/workflow.png',
        'static/description/dashboard.png',
        'static/description/designer.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

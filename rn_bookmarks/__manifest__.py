# -*- coding: utf-8 -*-
{
    'name': 'Universal Bookmark',
    'version': '19.0.1.2.0',
    'category': 'Productivity',
    'summary': 'Bookmark any Odoo record and open it instantly from a personal sidebar',
    'description': """
Universal Bookmark for Odoo 19 Community
=========================================

Never search for the same record twice.

* One-click bookmark on form, list, and Kanban views
* Personal sidebar with search, pins, favorites, and recent
* Drag-and-drop ordering in the sidebar
* Folders, colors, tags, and notes
* Ctrl+B hotkey on any record form
* List view and menu bookmarks
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
            'rn_bookmarks/static/src/bookmark_helpers.js',
            'rn_bookmarks/static/src/bookmarks_systray.js',
            'rn_bookmarks/static/src/bookmarks_sidebar.scss',
            'rn_bookmarks/static/src/bookmark_toggle.xml',
            'rn_bookmarks/static/src/bookmark_toggle.js',
            'rn_bookmarks/static/src/list_kanban_bookmark.xml',
            'rn_bookmarks/static/src/list_renderer_patch.js',
            'rn_bookmarks/static/src/kanban_record_patch.js',
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

# -*- coding: utf-8 -*-
{
    'name': 'Smart Color Tags',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Highlight records in list and Kanban views with configurable color rules on any model',
    'description': """
ARMORA Smart Color Tags for Odoo 19 Community
=============================================

Generic color rule engine for any Odoo model.

* Administrator-defined rules with domain conditions
* Priority-based rule matching
* Colored badges, icons, and row accents in list and Kanban views
* Works on CRM, sales, purchases, invoices, stock, HR, projects, and custom models
* Cached rule evaluation for responsive list pages
* Multi-company aware
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 56,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
        'account',
        'crm',
        'purchase',
        'stock',
        'hr',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/color_rule_data.xml',
        'views/color_rule_views.xml',
        'views/inherited_list_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_smart_color_tags/static/src/color_tags.scss',
            'rn_smart_color_tags/static/src/color_tags_service.js',
            'rn_smart_color_tags/static/src/list_renderer_patch.js',
            'rn_smart_color_tags/static/src/kanban_renderer_patch.js',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_smart_color_tags_form.png',
        'static/description/screenshot_smart_color_tags_list.png',
        'static/description/screenshot_smart_color_tags_dashboard.png',
        'static/description/screenshot_smart_color_tags_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

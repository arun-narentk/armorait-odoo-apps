# -*- coding: utf-8 -*-
{
    'name': 'Visual Enhancer',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Emoji status, badges, icons, and color accents for list and Kanban views',
    'description': """
ARMORA Visual Enhancer for Odoo 19 Community
============================================

Complete visual UX toolkit for Odoo list and Kanban views.

* Emoji status maps for selection fields (Paid, Draft, Hot, Overdue)
* Priority-based color rules with domain conditions
* Icons and colored badges on any model
* Row accents in list views and card highlights in Kanban
* Works on sales, invoices, CRM, stock, HR, projects, and custom models
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 58,
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
        'data/visual_status_data.xml',
        'views/color_rule_views.xml',
        'views/visual_status_views.xml',
        'views/inherited_list_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_visual_enhancer/static/src/color_tags.scss',
            'rn_visual_enhancer/static/src/color_tags_service.js',
            'rn_visual_enhancer/static/src/list_renderer_patch.js',
            'rn_visual_enhancer/static/src/kanban_renderer_patch.js',
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

# -*- coding: utf-8 -*-
{
    'name': 'Smart Notes',
    'version': '19.0.1.1.0',
    'category': 'Productivity',
    'summary': 'Context-aware sticky notes on any business document with pins, mentions, and reminders',
    'description': """
Smart Notes for Odoo 19 Community
=================================

Attach colorful sticky notes to any business document. Pin important reminders,
mention teammates, and keep critical customer context visible without opening
the chatter.

Features
--------

* Context-aware notes on Sale Orders, Purchase Orders, Invoices, CRM Leads,
  Contacts, Products, and Employees
* Color-coded cards with icons and priorities
* Pin, edit, delete, and quick templates from the document panel
* User mentions with notifications
* Reminders that create activities automatically
* Kanban, list, and search views with pinned and mention filters
* Reusable admin templates and one-click quick notes
* Private, team, and manager visibility controls
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 8.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 48,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
        'purchase',
        'account',
        'crm',
        'contacts',
        'product',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/note_template_data.xml',
        'views/smart_note_views.xml',
        'views/inherited_form_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
        'demo/demo_sale_order_notes.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_smart_notes/static/src/smart_notes_panel.scss',
            'rn_smart_notes/static/src/smart_notes_panel.xml',
            'rn_smart_notes/static/src/smart_notes_panel.js',
        ],
    },
                    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_smart_notes_form.png',
        'static/description/screenshot_smart_notes_list.png',
        'static/description/screenshot_smart_notes_dashboard.png',
        'static/description/screenshot_smart_notes_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

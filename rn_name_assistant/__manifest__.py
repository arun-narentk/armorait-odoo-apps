# -*- coding: utf-8 -*-
{
    'name': 'Name Assistant',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Generate professional, consistent names using configurable naming rules',
    'description': """
ARMORA Name Assistant for Odoo 19 Community
===========================================

Generate professional, consistent names for products, contacts, projects, and more
using configurable naming rules. No external API required.

Features
--------

* Configurable templates per model with priority and optional conditions
* Multiple ranked suggestions from sequence templates
* Product naming fields: brand, series, model, color, capacity, material, variant
* Heuristic suggestions for contacts, CRM leads, projects, and tasks
* Live preview, duplicate word cleanup, title case, and abbreviation expansion
* Batch name generation from list views with CSV export
* Multi-company aware configuration
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 7.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 52,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'product',
        'crm',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/abbreviation_data.xml',
        'data/name_template_data.xml',
        'views/name_template_views.xml',
        'views/inherited_form_views.xml',
        'views/menu.xml',
        'wizard/name_generator_wizard_views.xml',
        'wizard/batch_generator_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/dashboard.png',
        'static/description/overview.png',
        'static/description/form.png',
        'static/description/list.png',
        'static/description/kanban.png',
        'static/description/wizard.png',
        'static/description/designer.png',
        'static/description/search.png',
        'static/description/settings.png',
        'static/description/report.png',
        'static/description/workflow.png',
        'static/description/mobile.png',
        'static/description/hero.gif',
        'static/description/dashboard.gif',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

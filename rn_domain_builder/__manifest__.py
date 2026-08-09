# -*- coding: utf-8 -*-
{
    'name': 'Domain Builder',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Build Odoo search domains using plain English instead of Python-like syntax',
    'description': """
ARMORA Domain Builder for Odoo 19 Community
===========================================

Turn plain-English filter descriptions into valid Odoo domains.

* Dictionary-driven rule engine (no AI dependency)
* Hybrid UI with live suggestions and preview
* Test domains with record counts
* Save favorite filters and history
* Configurable word to field mappings per model
* Supports Sale Orders, Invoices, Products, CRM, Contacts, and more
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
        'product',
        'crm',
        'contacts',
        'hr',
        'purchase',
        'stock',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/domain_dictionary_data.xml',
        'views/domain_builder_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_domain_builder_form.png',
        'static/description/screenshot_domain_builder_list.png',
        'static/description/screenshot_domain_builder_dashboard.png',
        'static/description/screenshot_domain_builder_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

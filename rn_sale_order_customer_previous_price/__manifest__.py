# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Customer Previous Price',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'See what you charged this customer last time, directly on quotation lines',
    'description': """
Sale Order Customer Previous Price
==================================

When a salesperson selects a product on a quotation or order line, show the
most recent unit price previously sold to that same customer (commercial
partner), with optional difference vs the current unit price.

* Latest confirmed order price for the same product
* Commercial partner aware
* Multi-company safe
* Multi-currency conversion
* Informational only: never changes Unit Price
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 5.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 53,
    'depends': [
        'sale_management',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

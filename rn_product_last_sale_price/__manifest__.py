# -*- coding: utf-8 -*-
{
    'name': 'Product Last Sale Price',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'See what this customer last paid for a product on the sale order line',
    'description': """
Product Last Sale Price
=======================

When a salesperson selects a customer and product on a quotation or order line,
show the effective unit price from that customer's most recent confirmed sale
of the same product.

* Latest confirmed sale only (draft/cancelled ignored)
* Effective price after line discount
* Commercial partner aware
* Multi-company and multi-currency safe
* UoM conversion into the current line UoM
* Informational only: never changes Unit Price
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'LGPL-3',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 57,
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

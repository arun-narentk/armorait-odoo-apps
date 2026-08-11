# -*- coding: utf-8 -*-
{
    'name': 'Customer Outstanding on Sale Order',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Show the customer receivable outstanding amount on every Sale Order',
    'description': """
Customer Outstanding on Sale Order
==================================

Display the selected customer's current outstanding receivable balance on the
Sale Order form so salespeople can see how much the customer already owes
before confirming.

* Uses Odoo Total Receivable (partner credit) from posted accounting entries
* Commercial partner aware
* Multi-company safe
* Preserves credit (negative) balances
* Works out of the box after install
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 5.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 54,
    'depends': [
        'sale',
        'account',
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

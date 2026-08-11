# -*- coding: utf-8 -*-
{
    'name': 'Product Last Purchase Price',
    'version': '19.0.1.0.0',
    'category': 'Purchases/Purchases',
    'summary': 'See last paid purchase price on products and purchase order lines',
    'description': """
Product Last Purchase Price
===========================

Answer "What did we pay last time?" on products and while creating purchase orders.

* Last purchase price, date, vendor, and PO on the product
* Previous purchase price on each purchase order line
* Price difference and % vs current unit price
* Vendor-specific previous price with fallback to any vendor
* Company-aware, informational warning on price increases
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
        'purchase',
    ],
    'data': [
        'views/product_views.xml',
        'views/purchase_order_views.xml',
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

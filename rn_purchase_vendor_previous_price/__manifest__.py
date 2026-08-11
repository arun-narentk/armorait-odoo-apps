# -*- coding: utf-8 -*-
{
    'name': 'Purchase Vendor Previous Price',
    'version': '19.0.1.0.0',
    'category': 'Purchases/Purchases',
    'summary': 'See what you paid this vendor last time, directly on purchase order lines',
    'description': """
Purchase Vendor Previous Price
==============================

When creating or editing a Purchase Order, show the previous purchase price
paid to the selected vendor for each product, plus the date of that purchase.

* Latest confirmed PO price for the same product and vendor
* Commercial partner aware
* Multi-company safe
* Currency and UoM conversion via standard Odoo helpers
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
    'sequence': 54,
    'depends': [
        'purchase',
    ],
    'data': [
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

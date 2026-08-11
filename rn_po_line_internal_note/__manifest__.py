# -*- coding: utf-8 -*-
{
    'name': 'PO Line Internal Note',
    'version': '19.0.1.0.0',
    'category': 'Purchases/Purchases',
    'summary': 'Internal notes on purchase order lines, never shared with vendors',
    'description': """
PO Line Internal Note
=====================

Add an Internal Note field on each Purchase Order line for buyer-only comments.

* Per-line text notes on the Purchase Order form
* Not included in vendor RFQ/PO reports, portal, or email templates
* No configuration required
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 5.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 55,
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

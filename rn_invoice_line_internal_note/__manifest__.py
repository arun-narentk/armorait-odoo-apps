# -*- coding: utf-8 -*-
{
    'name': 'Invoice Line Internal Note',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Internal notes on invoice and bill lines, never printed for customers',
    'description': """
Invoice Line Internal Note
==========================

Add an Internal Note field on each invoice/bill line for internal comments.

* Works on customer invoices, credit notes, vendor bills, and refunds
* Not included in customer/vendor PDF reports, portal, or email templates
* No impact on totals, taxes, or posting
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
    'sequence': 59,
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_line_views.xml',
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

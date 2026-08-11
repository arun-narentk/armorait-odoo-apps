# -*- coding: utf-8 -*-
{
    'name': 'Quotation Expiry Countdown',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'See how much time is left before a quotation expires',
    'description': """
Quotation Expiry Countdown
==========================

Show a clear countdown next to the quotation Expiration date:

* Expires in X days / hours / minutes
* Expires today
* Expired X days ago

Also adds list-view countdown, urgency colours, and search filters
(Expiring Today, Expiring Within 24 Hours, Expired Quotations).
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 5.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 58,
    'depends': [
        'sale',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_quotation_expiry_countdown/static/src/scss/quotation_expiry_countdown.scss',
            'rn_quotation_expiry_countdown/static/src/js/quotation_expiry_countdown_field.js',
            'rn_quotation_expiry_countdown/static/src/xml/quotation_expiry_countdown_field.xml',
        ],
    },
    'demo': [],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

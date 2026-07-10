{
    'name': 'Arabic Tooltip',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Hover Arabic translations for backend labels and a reusable field widget',
    'description': """
Arabic Tooltip
==============

Reusable Arabic hover-translation system for the Odoo backend:

* A global service that adds Arabic tooltips to standard form/list labels.
* A field widget ``rn_arabic_hint`` that shows a custom Arabic tooltip on the
  field value and its label.

Arabic text is taken from Odoo's standard translation when the Arabic language
is installed, otherwise it falls back to a built-in accounting dictionary.
""",
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'depends': ['web', 'account'],
    'data': [
        'views/account_move_arabic_hint_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_arabic_tooltip/static/src/arabic_tooltip.scss',
            'rn_arabic_tooltip/static/src/arabic_label_tooltips.js',
            'rn_arabic_tooltip/static/src/arabic_hint_field.js',
            'rn_arabic_tooltip/static/src/arabic_hint_field.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
}

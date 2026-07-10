{
    'name': 'Arabic Tooltip',
    'version': '19.0.1.1.0',
    'category': 'Tools',
    'summary': 'Arabic hover translations for Odoo backend labels and the rn_arabic_hint field widget',
    'description': """
Arabic Tooltip for Odoo 19 Community
====================================

Arabic hover translations for Odoo backend labels and field values. Built for
bilingual finance teams in Saudi Arabia and GCC who run Odoo in English but need
accurate Arabic terminology on demand.

Features
--------

✓ Global backend label tooltips on forms and lists
✓ Reusable rn_arabic_hint field widget
✓ Uses Odoo standard Arabic translations when installed
✓ Built-in accounting fallback dictionary
✓ Demo on customer invoice fields
✓ OWL 2 service with cached lookups
✓ No UI language switch required

Ideal for finance, shared services, and Odoo partners delivering Arabic-ready
accounting on Odoo 19 Community.
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
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/workflow.png',
        'static/description/dashboard.png',
        'static/description/monitoring.png',
        'static/description/execution.png',
    ],
}

{
    'name': 'Arabic Tooltip',
    'version': '19.0.1.2.0',
    'category': 'Tools',
    'summary': 'Hover Arabic translations for backend labels and a reusable field widget',
    'description': """
Arabic hover translations for Odoo backend labels and field values. Global
label tooltips, rn_arabic_hint field widget, Odoo translation support, and an
accounting fallback dictionary for bilingual Saudi and GCC teams.
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
        'static/description/designer.png',
    ],
}

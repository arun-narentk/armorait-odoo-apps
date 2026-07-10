{
    'name': 'Saudi Finance Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Premium Saudi finance dashboard with KPIs in SAR, VAT, cash and top customers',
    'description': """
Saudi Finance Dashboard
=======================

Custom finance dashboard tailored for Saudi Arabia clients.
Shows net revenue, VAT collected (15%), cash position, outstanding receivables,
invoiced-by-month trend, and top customers, all in the company currency (SAR).
""",
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'depends': ['account', 'web', 'rn_arabic_tooltip'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_saudi_dashboard/static/src/dashboard.scss',
            'rn_saudi_dashboard/static/src/dashboard.js',
            'rn_saudi_dashboard/static/src/dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
}

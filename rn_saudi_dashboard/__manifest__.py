{
    'name': 'Saudi Finance Dashboard',
    'version': '19.0.1.2.0',
    'category': 'Accounting',
    'summary': 'Premium Saudi finance dashboard with KPIs in SAR, VAT, cash and top customers',
    'description': """
Premium Saudi finance dashboard for Odoo 19 Community with SAR KPIs, VAT,
receivables, payables, cash, compliance panels, trend charts, and bilingual OWL
dashboard for finance teams and ERP partners.
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
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 39.0,
    'live_test_url': 'https://www.armorait.com',
        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/dashboard.png',
        'static/description/overview.png',
        'static/description/form.png',
        'static/description/list.png',
        'static/description/kanban.png',
        'static/description/wizard.png',
        'static/description/designer.png',
        'static/description/search.png',
        'static/description/settings.png',
        'static/description/report.png',
        'static/description/workflow.png',
        'static/description/mobile.png',
    ],
}

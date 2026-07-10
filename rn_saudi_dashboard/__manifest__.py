{
    'name': 'Saudi Finance Dashboard',
    'version': '19.0.1.1.0',
    'category': 'Accounting',
    'summary': 'Premium Saudi finance dashboard with SAR KPIs, 15% VAT, cash, compliance, and top customers',
    'description': """
Saudi Finance Dashboard for Odoo 19 Community
=============================================

Premium finance dashboard tailored for Saudi Arabia clients. See net revenue, VAT
collected at 15%, cash position, receivables, payables, overdue payments, profit
estimate, compliance panels, invoiced-by-month trend, and top customers in SAR.

Features
--------

✓ 8 clickable finance KPI cards with drill-down
✓ Saudi compliance section for VAT and invoice readiness
✓ VAT collected vs VAT paid comparison
✓ Latest Saudi invoice QR preview
✓ Invoiced-by-month trend chart
✓ Top customers and top invoices tables
✓ Bilingual English and Arabic labels
✓ RTL layout and language toggle
✓ One-click invoice, bill, and report actions
✓ OWL 2 dashboard for Odoo 19 Community

Ideal for Saudi finance teams, ERP partners, and bilingual operations running Odoo
Accounting on Community.
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
        'static/description/workflow.png',
        'static/description/monitoring.png',
        'static/description/execution.png',
    ],
}

# -*- coding: utf-8 -*-
{
    'name': 'Profit Guard',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Margin protection and dead stock intelligence',
    'description': """
ProfitGuard 19 – Dead Stock & Margin Intelligence

**Dead Stock Intelligence**
- Per-product: days without movement, status (Healthy / Slow Moving / Dead Stock).
- Configurable thresholds (e.g. 90 days = Slow, 180 days = Dead).
- Capital locked (qty × cost), carrying cost estimate.
- Optional clearance discount suggestion for dead stock.

**Margin Guard**
- Real margin per sale order line: (price - cost) / price × 100.
- Status: Safe / Warning / Danger from configurable thresholds.
- Danger → block confirmation; override wizard with reason and approver.
- Violations logged in chatter and margin_violation_log.

**Dashboard**
- Inventory & Margin Intelligence: dead stock value, capital locked, top risk products, margin violations, margin trend, inventory aging.

Requires: Odoo 19, Sales, Stock, Accounting, Mail.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'depends': [
        'sale_management',
        'stock',
        'account',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/dashboard_views.xml',
        'views/margin_violation_log_views.xml',
        'views/dead_stock_log_views.xml',
        'wizards/margin_override_wizard_views.xml',
        'wizards/clearance_discount_wizard_views.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/overview.png',
        'static/description/dashboard.png',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 39.99,
    'live_test_url': 'https://www.armorait.com',
}

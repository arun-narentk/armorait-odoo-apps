# -*- coding: utf-8 -*-
{
    'name': 'Jewellery ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Jewellery',
    'summary': 'Metal specs, job work, karigar, orders, repairs, gold rates, POS hooks',
    'description': """
ARMORA Jewellery ERP Core for Odoo 19 Community
===============================================

High-value vertical for retail jewellers, manufacturers, and multi-branch chains.

Phase 1 (rn_jewellery_core) delivers:

* Jewellery product master: metal, purity, weights, stones, hallmark, barcode
* Gold, silver, platinum rate management
* Karigar registry and job cards
* Job work: issue gold, production, receive, QC, stock
* Custom customer orders with advances and delivery tracking
* Repair orders: polishing, stone replacement, resizing
* Customer CRM: purchase history, loyalty, occasions
* Manufacturing and retail OWL dashboards
* AI hooks: design search, pricing, demand forecast, fraud flags (heuristic)

Roadmap: POS integration, RFID, weighing scale, label printing, mobile app.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 70,
    'depends': [
        'base',
        'mail',
        'web',
        'account',
        'stock',
        'product',
        'purchase',
        'sale',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/metal_purity_data.xml',
        'views/item_views.xml',
        'views/rate_views.xml',
        'views/karigar_views.xml',
        'views/job_views.xml',
        'views/order_views.xml',
        'views/repair_views.xml',
        'views/customer_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/job_issue_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_jewellery_core/static/src/scss/jewellery_core.scss',
            'rn_jewellery_core/static/src/xml/manufacturing_dashboard.xml',
            'rn_jewellery_core/static/src/xml/retail_dashboard.xml',
            'rn_jewellery_core/static/src/js/manufacturing_dashboard.js',
            'rn_jewellery_core/static/src/js/retail_dashboard.js',
        ],
    },
                        'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_jewellery_core_form.png',
        'static/description/screenshot_jewellery_core_list.png',
        'static/description/screenshot_jewellery_core_dashboard.png',
        'static/description/screenshot_jewellery_core_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

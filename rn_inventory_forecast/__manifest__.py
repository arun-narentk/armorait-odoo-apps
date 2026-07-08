# -*- coding: utf-8 -*-
{
    'name': 'ARMORA Inventory Forecast',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Demand forecasting, safety stock, ABC/XYZ/FSN, and inventory planning for Odoo 19',
    'description': """
ARMORA Inventory Forecast for Odoo 19 Community
==========================================

Intelligent inventory planning: demand forecast, safety stock,
reorder points, ABC/XYZ/FSN analysis, smart alerts, and OWL dashboard.

Phase 1 delivers the installable framework with service-layer
architecture, models, security, menus, scheduled jobs, and a live
dashboard shell. AI forecasting arrives in later releases.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 39.99,
    'sequence': 38,
    'depends': [
        'base',
        'mail',
        'web',
        'stock',
        'purchase',
        'sale_management',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/cron.xml',
        'data/forecast_data.xml',
        'views/forecast_views.xml',
        'views/analysis_views.xml',
        'views/alert_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/forecast_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_inventory_forecast/static/src/scss/inventory_forecast.scss',
            'rn_inventory_forecast/static/src/xml/forecast_dashboard.xml',
            'rn_inventory_forecast/static/src/js/forecast_dashboard.js',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

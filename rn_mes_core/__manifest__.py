# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing MES',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Shop-floor MES: tablet execution, barcode, quality, downtime, OEE, IoT hooks',
    'description': """
ARMORA Manufacturing MES for Odoo 19 Community
==============================================

Shop-floor Manufacturing Execution System between ERP planning and production.

Phase 1 (rn_mes_core) delivers:

* Production tablet / kiosk UI for operators
* Work order start, pause, resume, complete workflow
* Scrap and reject quantity capture
* Barcode scan logging for materials, WOs, operators, machines
* Quality inspection checklists with pass/fail and photos
* Downtime tracking with reason codes
* OEE snapshots (availability, performance, quality)
* Machine device registry and IoT reading hooks (MQTT/OPC UA ready)
* Operator session and digital work instruction links
* OWL shop-floor dashboard and plant manager KPIs

Roadmap: PLC integration, scheduling board, predictive maintenance AI,
tool management, shift handover, energy monitoring, AI root cause analysis.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 249.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 52,
    'depends': [
        'base',
        'mail',
        'web',
        'mrp',
        'stock',
        'hr',
        'hr_attendance',
        'barcodes',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/downtime_reason_data.xml',
        'views/terminal_views.xml',
        'views/session_views.xml',
        'views/quality_views.xml',
        'views/downtime_views.xml',
        'views/machine_views.xml',
        'views/oee_views.xml',
        'views/workorder_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/barcode_scan_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_mes_core/static/src/scss/mes_core.scss',
            'rn_mes_core/static/src/xml/mes_tablet.xml',
            'rn_mes_core/static/src/xml/mes_dashboard.xml',
            'rn_mes_core/static/src/js/mes_tablet.js',
            'rn_mes_core/static/src/js/mes_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/workflow.png',
        'static/description/dashboard.png',
        'static/description/designer.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

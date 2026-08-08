# -*- coding: utf-8 -*-
{
    'name': 'Record Timeline',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Visual timeline history for sales, purchases, invoices, and CRM leads',
    'description': """
ARMORA Record Timeline for Odoo 19 Community
============================================

Answer "What happened to this record?" with a visual GitHub-style timeline.

* Supported documents: sale orders, purchase orders, invoices, CRM leads
* Automatic event logging on create and state changes
* Configurable timeline templates per model and state
* Smart button and notebook timeline widget with filters
* Export timeline to PDF
* Lazy loading with 50 events per page
* Multi-company security and manager configuration
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 8.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 56,
    'depends': [
        'base',
        'mail',
        'web',
        'sale_management',
        'purchase',
        'account',
        'crm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/timeline_template_data.xml',
        'views/timeline_event_views.xml',
        'views/timeline_template_views.xml',
        'views/settings_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/crm_lead_views.xml',
        'views/menu.xml',
        'report/timeline_report_templates.xml',
        'report/timeline_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_record_timeline/static/src/scss/timeline_widget.scss',
            'rn_record_timeline/static/src/xml/timeline_widget.xml',
            'rn_record_timeline/static/src/js/timeline_widget.js',
        ],
    },
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
        'static/description/hero.gif',
        'static/description/dashboard.gif',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'AI Workflow Builder',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Automation',
    'summary': 'Visual automation platform: triggers, conditions, actions, AI workflow builder',
    'description': """
ARMORA AI Workflow Builder for Odoo 19 Community
================================================

Automation engine for your Odoo ecosystem (Zapier/Make style, native to Odoo).

Phase 1 (rn_workflow_builder) delivers:

* Workflow definitions with trigger, condition, and action nodes
* Execution engine with run history and error logs
* Core triggers: record created, record updated, scheduled, webhook
* Core conditions: field rules, amount thresholds, domain filters
* Core actions: create/update records, send email, start approval hook, call webhook
* Connector registry (Odoo models, email, webhook; WhatsApp/MES ready)
* AI workflow draft from plain English (heuristic parser)
* AI validation: loops, missing steps, permission warnings
* Monitoring dashboard: success rate, failures, retry queue
* Example hooks on sales orders and purchase orders

Companion to rn_approval_engine (approvals) and platform for OCR, MES, WhatsApp modules.

Roadmap: drag-and-drop canvas, external connectors, AI optimization, workflow marketplace.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 48,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
        'purchase',
        'account',
        'hr',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/connector_data.xml',
        'data/workflow_template_data.xml',
        'views/workflow_views.xml',
        'views/node_views.xml',
        'views/execution_views.xml',
        'views/connector_views.xml',
        'views/template_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/build_from_text_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_workflow_builder/static/src/scss/workflow_builder.scss',
            'rn_workflow_builder/static/src/xml/workflow_designer.xml',
            'rn_workflow_builder/static/src/xml/workflow_dashboard.xml',
            'rn_workflow_builder/static/src/js/workflow_designer.js',
            'rn_workflow_builder/static/src/js/workflow_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

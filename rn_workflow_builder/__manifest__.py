# -*- coding: utf-8 -*-
{
    'name': 'AI Automation Platform',
    'version': '19.0.1.1.0',
    'category': 'Automation',
    'summary': 'Enterprise AI Automation Platform for Odoo with Visual Workflows, AI Builder, Approvals, Webhooks, and Smart Connectors',
    'description': """
ARMORA AI Automation Platform for Odoo 19 Community
=====================================================

Enterprise AI automation platform for Odoo. Orchestrate business processes with
visual workflows, AI builder, approvals, webhooks, and smart connectors in one
native layer.

Go beyond a basic workflow tool. Unify OCR, WhatsApp, IoT and MES signals, AI
agents, and external systems under a single ARMORA automation brand for process
orchestration across sales, purchase, inventory, HR, accounting, and CRM.

Visual workflow builder for workflow automation and business automation across your
Odoo stack. A practical Zapier alternative and Make.com alternative for teams that
want Odoo automation without external tools.

Features
--------

✓ Visual Workflow Builder
✓ AI Workflow Generation
✓ AI Workflow Validation
✓ Trigger Engine
✓ Conditional Logic
✓ Scheduled Automation
✓ Incoming Webhooks
✓ Outgoing Webhooks
✓ Approval Integration
✓ Smart Connector Framework
✓ Retry Queue
✓ Error Logs
✓ Execution Timeline
✓ Sales Automation
✓ Purchase Automation
✓ Inventory Automation
✓ HR Automation
✓ Accounting Automation
✓ Native Odoo Architecture

Upcoming
--------

• Drag and Drop Canvas
• AI Optimization and AI Agents
• WhatsApp Automation
• OCR Automation
• IoT and MES Connectors
• Marketplace
• SAP Connector
• Shopify Connector
• Power BI Connector
• Google Sheets
• Slack
• Microsoft Teams
• REST API
• MQTT

Prebuilt starter workflows for sales approval, purchase approval, invoicing,
lead assignment, stock reorder, leave and expense approval, customer welcome,
and follow-up reminders are included at install.
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
        'crm',
        'hr_holidays',
        'hr_expense',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/connector_data.xml',
        'data/workflow_template_data.xml',
        'data/workflow_starter_data.xml',
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
        'static/description/workflow.png',
        'static/description/dashboard.png',
        'static/description/designer.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

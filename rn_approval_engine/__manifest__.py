# -*- coding: utf-8 -*-
{
    'name': 'Workflow Approval Engine',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Universal approval workflows for PO, bills, expenses, and custom documents',
    'description': """
ARMORA Workflow Automation and Approval Engine for Odoo 19 Community
====================================================================

Configurable multi-level and parallel approvals without custom code per document.

Phase 1 (rn_approval_engine) delivers:

* Visual workflow templates with unlimited stages
* Amount, department, and category routing rules
* Sequential and parallel approval levels
* Conditional stage requirements (e.g. legal for new vendors)
* Approval delegation when managers are away
* Approve, reject, request changes with comments and attachments
* Full approval history and audit trail
* Email notifications to pending approvers
* AI risk hints (amount vs history, duplicate warnings)
* OWL dashboard: pending, SLA, bottlenecks
* Hooks for purchase orders and vendor bills

Roadmap: drag-and-drop builder, WhatsApp, digital signature, mobile actions,
workflow automation beyond approval (auto PO, vendor email, payment scheduling).
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 55,
    'depends': [
        'base',
        'mail',
        'web',
        'account',
        'purchase',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'views/workflow_views.xml',
        'views/rule_views.xml',
        'views/request_views.xml',
        'views/delegation_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/submit_approval_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_approval_engine/static/src/scss/approval_engine.scss',
            'rn_approval_engine/static/src/xml/approval_dashboard.xml',
            'rn_approval_engine/static/src/js/approval_dashboard.js',
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

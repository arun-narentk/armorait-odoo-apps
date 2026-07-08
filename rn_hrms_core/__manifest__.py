# -*- coding: utf-8 -*-
{
    'name': 'HRMS Core',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Employee lifecycle, org structure, and HR operations base',
    'description': """
ARMORA HRMS Core for Odoo 19 Community
======================================

Modern HR & Payroll platform foundation for small and medium businesses.

rn_hrms_core provides shared services used by companion modules:
employee extensions, branches, designations, documents, announcements,
generic approval engine, notifications, OWL HR dashboard, API hooks,
and SaaS-ready subscription settings.

Install specialized add-ons later: attendance, leave, payroll,
recruitment, performance, portal, and more.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 49.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 40,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'hr',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/hrms_data.xml',
        'data/cron.xml',
        'views/branch_views.xml',
        'views/designation_views.xml',
        'views/employee_views.xml',
        'views/document_views.xml',
        'views/announcement_views.xml',
        'views/approval_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/employee_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hrms_core/static/src/scss/hrms.scss',
            'rn_hrms_core/static/src/xml/hrms_dashboard.xml',
            'rn_hrms_core/static/src/js/hrms_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/overview.png',
        'static/description/dashboard.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

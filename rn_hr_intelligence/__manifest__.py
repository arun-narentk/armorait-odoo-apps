# -*- coding: utf-8 -*-
{
    'name': 'Workforce Intelligence',
    'version': '19.0.1.0.1',
    'category': 'Human Resources',
    'summary': 'HR intelligence: payroll analytics, overtime, attrition, compliance KPIs',
    'description': """
ARMORA Workforce Intelligence for Odoo 19 Community
===================================================

HR command center beyond payroll tables: workforce cost, overtime, attendance,
attrition, compliance, and AI narrative insights.

Phase 1 (rn_hr_intelligence) delivers:

* Executive payroll overview (gross, net estimates, overtime, compliance hooks)
* Monthly payroll and department-wise cost analytics
* Overtime hours and cost tracking with trends
* Attendance cost linkage (paid days, leave, absenteeism hooks)
* Attrition dashboard (hires, resignations, turnover rate)
* Cost center and branch allocation framework
* Data quality checks for incomplete HR records
* AI workforce summary insights
* OWL executive dashboard

Works with hr contracts and attendance on Community. Optional payslip
integration when payroll module is installed.

Roadmap: salary forecast, anomaly detection, AI chat, multi-company
consolidation, recruitment cost analytics.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 42,
    'depends': [
        'base',
        'mail',
        'web',
        'hr',
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/payroll_snapshot_views.xml',
        'views/overtime_views.xml',
        'views/attrition_views.xml',
        'views/insight_views.xml',
        'views/quality_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hr_intelligence/static/src/scss/hr_intelligence.scss',
            'rn_hr_intelligence/static/src/xml/hr_dashboard.xml',
            'rn_hr_intelligence/static/src/js/hr_dashboard.js',
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

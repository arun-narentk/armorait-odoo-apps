# -*- coding: utf-8 -*-
{
    'name': 'Hospital ERP',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Patients, appointments, and hospital operations foundation',
    'description': """
ARMORA Hospital ERP Core for Odoo 19 Community
==============================================

Affordable hospital / clinic foundation for 5-100 bed facilities,
multi-specialty clinics, dental, diagnostic, and specialty centers.

rn_hms_core provides shared base models and services used by companion
modules: patient, doctor, appointment, billing, pharmacy, lab, IPD,
insurance, nursing, and patient portal.

Integrates with Odoo Contacts, Calendar, and Accounting rather than
re-implementing ERP foundations inside HMS.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 42,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'calendar',
        'portal',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/hms_data.xml',
        'data/cron.xml',
        'views/department_views.xml',
        'views/doctor_views.xml',
        'views/patient_views.xml',
        'views/ward_views.xml',
        'views/bed_views.xml',
        'views/appointment_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'report/patient_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hms_core/static/src/scss/hms.scss',
            'rn_hms_core/static/src/xml/hms_dashboard.xml',
            'rn_hms_core/static/src/js/hms_dashboard.js',
        ],
    },
                    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_hms_core_form.png',
        'static/description/screenshot_hms_core_list.png',
        'static/description/screenshot_hms_core_dashboard.png',
        'static/description/screenshot_hms_core_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

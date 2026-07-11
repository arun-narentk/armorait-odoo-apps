# -*- coding: utf-8 -*-
{
    'name': 'Hospital ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Patient management, appointments, EMR, billing hooks for clinics and hospitals',
    'description': """
ARMORA Hospital ERP Core for Odoo 19 Community
==============================================

Foundation for 20-200 bed hospitals, multi-specialty clinics, and specialty centers.

Phase 1 (rn_hospital_core) delivers:

* Patient registration with UHID, family, allergies, chronic conditions
* Insurance and consent records
* Appointment booking, queue tokens, doctor schedules
* EMR encounters: consultation notes, diagnoses, prescriptions
* Doctor dashboard: today schedule, waiting patients, history
* Basic inpatient: wards, beds, admissions (foundation)
* Hospital billing lines linked to accounting
* OWL hospital and doctor dashboards
* AI insight hooks: scribe, discharge summary, analytics (heuristic)

Roadmap: pharmacy, laboratory, radiology, OT, specialty verticals (dental, eye).
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 249.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 58,
    'depends': [
        'base',
        'mail',
        'web',
        'website',
        'portal',
        'account',
        'hr',
        'stock',
        'product',
        'calendar',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/department_data.xml',
        'views/patient_views.xml',
        'views/appointment_views.xml',
        'views/emr_views.xml',
        'views/inpatient_views.xml',
        'views/billing_views.xml',
        'views/doctor_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/appointment_book_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hospital_core/static/src/scss/hospital_core.scss',
            'rn_hospital_core/static/src/xml/hospital_dashboard.xml',
            'rn_hospital_core/static/src/xml/doctor_dashboard.xml',
            'rn_hospital_core/static/src/js/hospital_dashboard.js',
            'rn_hospital_core/static/src/js/doctor_dashboard.js',
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

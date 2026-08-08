# -*- coding: utf-8 -*-
{
    'name': 'Dental ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Patients, appointments, odontogram, treatment plans, lab, billing hooks',
    'description': """
ARMORA Dental ERP Core for Odoo 19 Community
============================================

Focused clinic operating system for dental practices and multi-chair clinics.

Phase 1 (rn_dental_core) delivers:

* Patient profiles: history, allergies, consent, family links
* Appointments: dentist schedule, chair allocation, reminders
* Dental charting: tooth records and odontogram data model
* Treatment plans with procedures, visits, costs, progress
* Procedure catalog and procedure-based billing hooks
* Lab workflow: crown, bridge, denture requests and turnaround
* Patient imaging: X-ray, CBCT, intraoral photo attachments
* Recall system for check-ups and follow-ups
* Clinic owner, dentist, and reception dashboards
* AI hooks: clinical notes draft, scheduling, recalls, revenue Q&A

Roadmap: visual odontogram widget, patient portal, insurance claims, imaging PACS.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 71,
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
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/procedure_data.xml',
        'views/patient_views.xml',
        'views/appointment_views.xml',
        'views/chart_views.xml',
        'views/treatment_views.xml',
        'views/lab_views.xml',
        'views/imaging_views.xml',
        'views/recall_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/appointment_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_dental_core/static/src/scss/dental_core.scss',
            'rn_dental_core/static/src/xml/clinic_dashboard.xml',
            'rn_dental_core/static/src/xml/dentist_dashboard.xml',
            'rn_dental_core/static/src/js/clinic_dashboard.js',
            'rn_dental_core/static/src/js/dentist_dashboard.js',
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
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

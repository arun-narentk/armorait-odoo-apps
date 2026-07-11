# -*- coding: utf-8 -*-
{
    'name': 'Veterinary ERP Core',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Pets, owners, appointments, vaccinations, surgery, grooming, boarding',
    'description': """
ARMORA Veterinary ERP Core for Odoo 19 Community
================================================

Modern platform for veterinary clinics and pet hospitals.

Phase 1 (rn_veterinary_core) delivers:

* Pet profiles: species, breed, weight, microchip, medical history
* Owner management with multiple pets per customer
* Appointments: consultation, vaccination, surgery, grooming, boarding
* Vaccination schedules and due-date reminders
* Medical records, prescriptions, lab results, imaging
* Surgery scheduling and recovery notes
* Grooming services and packages
* Boarding: kennels, check-in/out, feeding schedules
* Clinic owner and veterinarian dashboards
* AI hooks: clinical notes, vaccination assistant, recalls, analytics

Roadmap: owner mobile app, pharmacy batch tracking, livestock module.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 72,
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
        'data/vaccine_data.xml',
        'views/owner_views.xml',
        'views/pet_views.xml',
        'views/appointment_views.xml',
        'views/vaccination_views.xml',
        'views/medical_views.xml',
        'views/surgery_views.xml',
        'views/grooming_views.xml',
        'views/boarding_views.xml',
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
            'rn_veterinary_core/static/src/scss/veterinary_core.scss',
            'rn_veterinary_core/static/src/xml/clinic_dashboard.xml',
            'rn_veterinary_core/static/src/xml/vet_dashboard.xml',
            'rn_veterinary_core/static/src/js/clinic_dashboard.js',
            'rn_veterinary_core/static/src/js/vet_dashboard.js',
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

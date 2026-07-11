# -*- coding: utf-8 -*-
{
    'name': 'AI School Operating System',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'AI school OS: admissions, fees, attendance, exams, homework, parent engagement',
    'description': """
ARMORA AI School Operating System for Odoo 19 Community
=======================================================

Not a generic school ERP. Automation and parent engagement for private schools.

Phase 1 (rn_school_core) delivers:

* Student profiles, parents, medical info, class allocation
* Admission workflow: enquiry, application, verification, approval
* Fee structures, installments, scholarships, invoice hooks
* Attendance (manual, QR-ready) with parent notification hooks
* Timetable and teacher schedules
* Exams, marks, grades, report card foundation
* Homework assignments and submissions
* School notices and parent portal hooks
* Principal, teacher, and parent dashboards
* AI report card comments, risk detection, academic analytics

Roadmap: transport GPS, library, hostel, face attendance, mobile app, WhatsApp.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 199.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 62,
    'depends': [
        'base',
        'mail',
        'web',
        'website',
        'portal',
        'account',
        'hr',
        'calendar',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/academic_year_data.xml',
        'views/student_views.xml',
        'views/admission_views.xml',
        'views/fee_views.xml',
        'views/attendance_views.xml',
        'views/timetable_views.xml',
        'views/exam_views.xml',
        'views/homework_views.xml',
        'views/notice_views.xml',
        'views/academic_views.xml',
        'views/teacher_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'wizard/admission_approve_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_school_core/static/src/scss/school_core.scss',
            'rn_school_core/static/src/xml/school_dashboard.xml',
            'rn_school_core/static/src/xml/teacher_dashboard.xml',
            'rn_school_core/static/src/js/school_dashboard.js',
            'rn_school_core/static/src/js/teacher_dashboard.js',
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

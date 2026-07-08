# -*- coding: utf-8 -*-
{
    'name': 'Attendance Face Recognition',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Biometric attendance with face matching and OWL kiosk',
    'description': """
HR Attendance Face Recognition for Odoo 19 Community
====================================================

Commercial-grade biometric attendance using face embeddings.

Architecture separates AI (detection, embedding, matching, anti-spoof)
from Odoo attendance business logic so engines (InsightFace, OpenCV,
ONNX) can be swapped without changing HR flows.

Phase 1: Module skeleton, security, menus, models, and service stubs.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 59.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 37,
    'depends': [
        'base',
        'mail',
        'web',
        'hr',
        'hr_attendance',
    ],
    'external_dependencies': {
        'python': ['numpy'],
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron.xml',
        'data/ir_config_parameter.xml',
        'views/employee_views.xml',
        'views/attendance_views.xml',
        'views/camera_views.xml',
        'views/dashboard_views.xml',
        'views/settings_views.xml',
        'views/wizard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_hr_attendance_face/static/src/scss/attendance_face.scss',
            'rn_hr_attendance_face/static/src/xml/face_dashboard.xml',
            'rn_hr_attendance_face/static/src/js/face_dashboard.js',
            'rn_hr_attendance_face/static/src/xml/face_kiosk.xml',
            'rn_hr_attendance_face/static/src/js/face_kiosk.js',
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

# -*- coding: utf-8 -*-
{
    'name': 'HR Resume AI Parser',
    'version': '1.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Parse resumes with AI and extract skills, experience, and match score',
    'description': """
        Async resume parsing: PDF extraction, AI-structured JSON, skill normalization,
        experience calculation, and job match score. Uses queue_job when available.
    """,
    'depends': [
        'hr_recruitment',
        'hr_skills',
        'mail',
        'web',
        'base',
    ],
    # Use 'pdfminer' (import name) so dependency works even when 'packaging' is not installed
    'external_dependencies': {
        'python': ['pdfminer'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/resume_parser_cron.xml',
        'data/skill_normalization_data.xml',
        'views/hr_applicant_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/hr_resume_bulk_upload_wizard_views.xml',
        'views/hr_resume_ai_parser_menus_views.xml',
    ],
    'author': 'ARMORAIT',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

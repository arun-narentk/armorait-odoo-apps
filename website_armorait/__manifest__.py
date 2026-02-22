# -*- coding: utf-8 -*-
{
    'name': 'ARMORAIT Website',
    'description': 'ARMORAIT ERP Business Solutions - Odoo IT company website',
    'category': 'Website',
    'version': '1.0',
    'depends': ['website'],
    'data': [
        'views/website_armorait_templates.xml',
        'data/website_armorait_pages.xml',
        'data/website_armorait_seo.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': 'Attachment Preview',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Preview PDFs, images, videos, audio, and text files inside Odoo without downloading',
    'description': """
ARMORA Attachment Preview for Odoo 19 Community
===============================================

Preview attachments directly inside Odoo forms and lists.

* PDF, image, video, audio, and text file preview
* Thumbnail strip on attachment widgets
* Hover preview for images and lightweight files
* Full-screen viewer with gallery navigation
* Respects Odoo access rights on every preview
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 60,
    'depends': [
        'base',
        'mail',
        'web',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inherited_form_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_attachment_preview/static/src/attachment_preview_field.scss',
            'rn_attachment_preview/static/src/attachment_preview_field.xml',
            'rn_attachment_preview/static/src/attachment_preview_field.js',
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

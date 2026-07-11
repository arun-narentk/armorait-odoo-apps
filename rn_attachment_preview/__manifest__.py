# -*- coding: utf-8 -*-
{
    'name': 'Attachment Preview',
    'version': '19.0.2.0.0',
    'category': 'Productivity',
    'summary': 'Preview PDFs, Office files, images, and media inside Odoo without downloading',
    'description': """
ARMORA Attachment Preview for Odoo 19 Community
===============================================

Preview attachments directly inside Odoo forms and lists.

* PDF, image, video, audio, text, and Office file preview
* Thumbnail strip with scheduled thumbnail generation
* OCR search across attachment text
* Word, Excel, and PowerPoint HTML preview engine
* PDF annotations with page notes
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
        'base_setup',
        'mail',
        'web',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/cron.xml',
        'views/inherited_form_views.xml',
        'views/rn_attachment_preview_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_attachment_preview/static/src/attachment_preview_field.scss',
            'rn_attachment_preview/static/src/preview_dialog.xml',
            'rn_attachment_preview/static/src/preview_dialog.js',
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

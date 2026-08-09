# -*- coding: utf-8 -*-
{
    'name': 'AI BIZ Promotion Landing',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Configurable AI BIZ website landing page with banner, benefits, and CTA',
    'description': """
ARMORA AI BIZ Promotion Landing for Odoo 19 Community
=====================================================

Publish a modern, mobile-first promotional landing page at /ai-biz.

* Backend-managed promotions and benefit cards
* Drag-and-drop benefit ordering
* Banner image, HTML copy, and CTA button
* Bootstrap 5 responsive layout with SCSS styling
* Multi-company aware records and access rights
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 9.99,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 62,
    'depends': [
        'base',
        'mail',
        'web',
        'website',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/promotion_views.xml',
        'views/benefit_views.xml',
        'views/menus.xml',
        'views/website_templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rn_ai_biz_promotion/static/src/scss/promotion.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/company_logo.png',
        'static/description/screenshot_ai_biz_promotion_form.png',
        'static/description/screenshot_ai_biz_promotion_list.png',
        'static/description/screenshot_ai_biz_promotion_dashboard.png',
        'static/description/screenshot_ai_biz_promotion_back.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

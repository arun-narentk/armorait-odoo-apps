# -*- coding: utf-8 -*-
{
    'name': 'AI Business Launch Core',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'AI business brief, site structure, pages, SEO, and Odoo publish hooks',
    'description': """
ARMORA AI Business Launch Core for Odoo 19 Community
====================================================

Turn a plain-language business description into a structured website project
with pages, content blocks, theme, SEO metadata, and Odoo integration hooks.
Positioned as an AI Business Launch Platform, not just a page generator.

Phase 1 (rn_ai_site_base) delivers:

* Business brief capture (type, location, tone, audience, keywords)
* Website project with multi-page structure
* Content blocks (hero, services, FAQ, contact, CTA, etc.)
* Theme presets (colors, fonts, layout style)
* SEO metadata per page (title, description, OG tags)
* Template-based site generation from brief (LLM-ready service layer)
* Publish workflow and Odoo website sync hooks
* Operations dashboard

Companion modules (roadmap): AI content, AI images, AI blog, forms, products,
publisher, chatbot, analytics, CRM auto-setup, standalone SaaS API.
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 149.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 59,
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/theme_presets.xml',
        'data/ir_config_parameter.xml',
        'views/brief_views.xml',
        'views/site_views.xml',
        'views/page_views.xml',
        'views/block_views.xml',
        'views/settings_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_ai_site_base/static/src/scss/ai_site.scss',
            'rn_ai_site_base/static/src/xml/ai_site_dashboard.xml',
            'rn_ai_site_base/static/src/js/ai_site_dashboard.js',
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

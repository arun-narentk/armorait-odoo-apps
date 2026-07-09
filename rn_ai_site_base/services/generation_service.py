# -*- coding: utf-8 -*-
"""Template-based site generation (LLM-ready)."""

import json
import logging

from odoo import models

_logger = logging.getLogger(__name__)

DEFAULT_PAGES = [
    ('home', 'Home', '/'),
    ('about', 'About Us', '/about'),
    ('services', 'Services', '/services'),
    ('gallery', 'Gallery', '/gallery'),
    ('testimonials', 'Testimonials', '/testimonials'),
    ('faq', 'FAQ', '/faq'),
    ('contact', 'Contact', '/contact'),
]

HERO_BY_TYPE = {
    'bakery': 'Fresh cakes and custom designs for every celebration',
    'salon': 'Look your best with expert styling and care',
    'restaurant': 'Authentic flavors served with warmth',
    'tuition': 'Quality coaching that helps students excel',
    'gym': 'Train smarter. Get stronger. Feel better.',
    'clinic': 'Trusted healthcare close to home',
    'hotel': 'Comfortable stays and memorable hospitality',
    'other': 'Professional services you can trust',
}


class RnAiSiteGenerationService(models.AbstractModel):
    """Generate site structure, pages, blocks, and SEO from a brief."""

    _name = 'rn.ai.site.generation.service'
    _description = 'AI Site Generation Service'

    def generate_from_brief(self, brief):
        theme = self._pick_theme(brief.business_type)
        site = self.env['rn.ai.site.site'].create({
            'name': f'{brief.business_name} Website',
            'brief_id': brief.id,
            'business_name': brief.business_name,
            'business_type': brief.business_type,
            'location': brief.location,
            'theme_id': theme.id,
            'primary_color': theme.primary_color,
            'secondary_color': theme.secondary_color,
            'font_heading': theme.font_heading,
            'font_body': theme.font_body,
            'company_id': brief.company_id.id,
            'state': 'ready',
        })
        for page_type, title, slug in DEFAULT_PAGES:
            page = self._create_page(site, brief, page_type, title, slug)
            self._create_blocks_for_page(page, brief)
        return site

    def _pick_theme(self, business_type):
        Theme = self.env['rn.ai.site.theme']
        theme = Theme.search([('code', '=', business_type)], limit=1)
        if not theme:
            theme = Theme.search([('code', '=', 'modern_blue')], limit=1)
        return theme

    def _create_page(self, site, brief, page_type, title, slug):
        seo_title = f'{title} | {brief.business_name}'
        if brief.location:
            seo_title = f'{title} | {brief.business_name} {brief.location}'
        keywords = brief.keywords or brief.location or brief.business_name
        return self.env['rn.ai.site.page'].create({
            'name': title,
            'slug': slug,
            'site_id': site.id,
            'page_type': page_type,
            'seo_title': seo_title,
            'seo_description': self._seo_description(brief, page_type),
            'og_title': seo_title,
            'og_description': brief.description[:160] if brief.description else seo_title,
            'structured_data_json': json.dumps(self._structured_data(site, brief, page_type)),
        })

    def _seo_description(self, brief, page_type):
        base = brief.description or f'{brief.business_name} offers quality services.'
        if page_type == 'contact':
            return f'Contact {brief.business_name} in {brief.location or "your area"}. Call or WhatsApp today.'
        return base[:155]

    def _structured_data(self, site, brief, page_type):
        if page_type != 'home':
            return {'@context': 'https://schema.org', '@type': 'WebPage', 'name': site.name}
        return {
            '@context': 'https://schema.org',
            '@type': 'LocalBusiness',
            'name': brief.business_name,
            'description': brief.description,
            'address': {'@type': 'PostalAddress', 'addressLocality': brief.location or ''},
            'telephone': brief.phone or '',
        }

    def _create_blocks_for_page(self, page, brief):
        Block = self.env['rn.ai.site.block']
        if page.page_type == 'home':
            Block.create({
                'name': 'Hero',
                'page_id': page.id,
                'block_type': 'hero',
                'sequence': 1,
                'headline': brief.business_name,
                'subheadline': HERO_BY_TYPE.get(brief.business_type, HERO_BY_TYPE['other']),
                'body_html': f'<p>{brief.description or ""}</p>',
                'cta_label': 'Contact Us',
                'cta_url': '/contact',
            })
            Block.create({
                'name': 'Services Preview',
                'page_id': page.id,
                'block_type': 'services',
                'sequence': 2,
                'headline': 'What We Offer',
                'body_html': self._services_html(brief),
            })
            Block.create({
                'name': 'CTA',
                'page_id': page.id,
                'block_type': 'cta',
                'sequence': 3,
                'headline': 'Ready to get started?',
                'cta_label': 'Get in Touch',
                'cta_url': '/contact',
            })
        elif page.page_type == 'about':
            Block.create({
                'name': 'About',
                'page_id': page.id,
                'block_type': 'about',
                'headline': f'About {brief.business_name}',
                'body_html': f'<p>{brief.description or ""}</p>',
            })
        elif page.page_type == 'services':
            Block.create({
                'name': 'Services',
                'page_id': page.id,
                'block_type': 'services',
                'headline': 'Our Services',
                'body_html': self._services_html(brief),
            })
        elif page.page_type == 'faq':
            Block.create({
                'name': 'FAQ',
                'page_id': page.id,
                'block_type': 'faq',
                'headline': 'Frequently Asked Questions',
                'body_html': self._faq_html(brief),
            })
        elif page.page_type == 'contact':
            Block.create({
                'name': 'Contact',
                'page_id': page.id,
                'block_type': 'contact',
                'headline': 'Contact Us',
                'body_html': self._contact_html(brief),
            })
            if brief.location:
                Block.create({
                    'name': 'Map',
                    'page_id': page.id,
                    'block_type': 'map',
                    'sequence': 2,
                    'headline': brief.location,
                })

    def _services_html(self, brief):
        items = [s.strip() for s in (brief.services or '').split(',') if s.strip()]
        if not items:
            items = ['Personalized service', 'Quality you can trust', 'Local expertise']
        lis = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ul>{lis}</ul>'

    def _faq_html(self, brief):
        loc = brief.location or 'our location'
        return (
            f'<p><strong>Where are you located?</strong><br/>We are based in {loc}.</p>'
            f'<p><strong>How can I reach you?</strong><br/>'
            f'Use the contact form or call {brief.phone or "us"}.</p>'
        )

    def _contact_html(self, brief):
        parts = []
        if brief.phone:
            parts.append(f'<p>Phone: {brief.phone}</p>')
        if brief.email:
            parts.append(f'<p>Email: {brief.email}</p>')
        if brief.whatsapp:
            parts.append(f'<p>WhatsApp: {brief.whatsapp}</p>')
        if brief.location:
            parts.append(f'<p>Location: {brief.location}</p>')
        return ''.join(parts) or '<p>We would love to hear from you.</p>'

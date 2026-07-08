# -*- coding: utf-8 -*-
"""Website pages with SEO metadata."""

from odoo import fields, models

PAGE_TYPES = [
    ('home', 'Home'),
    ('about', 'About'),
    ('services', 'Services / Products'),
    ('gallery', 'Gallery'),
    ('testimonials', 'Testimonials'),
    ('faq', 'FAQ'),
    ('contact', 'Contact'),
    ('blog', 'Blog'),
    ('policy', 'Policy'),
]


class RnAiSitePage(models.Model):
    """Single page in an AI-generated website."""

    _name = 'rn.ai.site.page'
    _description = 'AI Site Page'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    slug = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    site_id = fields.Many2one(
        'rn.ai.site.site',
        required=True,
        ondelete='cascade',
        index=True,
    )
    page_type = fields.Selection(selection=PAGE_TYPES, default='home', required=True)
    is_published = fields.Boolean(default=True)
    block_ids = fields.One2many('rn.ai.site.block', 'page_id', string='Content Blocks')
    seo_title = fields.Char(string='SEO Title')
    seo_description = fields.Text(string='Meta Description')
    og_title = fields.Char(string='Open Graph Title')
    og_description = fields.Text(string='Open Graph Description')
    structured_data_json = fields.Text(string='Structured Data (JSON-LD)')
    company_id = fields.Many2one(
        related='site_id.company_id',
        store=True,
        index=True,
    )

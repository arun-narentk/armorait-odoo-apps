# -*- coding: utf-8 -*-
"""Content blocks within pages."""

from odoo import fields, models

BLOCK_TYPES = [
    ('hero', 'Hero Banner'),
    ('about', 'About Section'),
    ('services', 'Services Grid'),
    ('products', 'Product Catalog'),
    ('gallery', 'Image Gallery'),
    ('testimonials', 'Testimonials'),
    ('faq', 'FAQ Accordion'),
    ('cta', 'Call to Action'),
    ('contact', 'Contact Form'),
    ('map', 'Google Maps'),
    ('footer', 'Footer'),
    ('text', 'Rich Text'),
]


class RnAiSiteBlock(models.Model):
    """Structured content block on a page."""

    _name = 'rn.ai.site.block'
    _description = 'AI Site Content Block'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    page_id = fields.Many2one(
        'rn.ai.site.page',
        required=True,
        ondelete='cascade',
        index=True,
    )
    site_id = fields.Many2one(
        related='page_id.site_id',
        store=True,
        index=True,
    )
    block_type = fields.Selection(selection=BLOCK_TYPES, default='text', required=True)
    headline = fields.Char()
    subheadline = fields.Char()
    body_html = fields.Html(string='Body Content')
    cta_label = fields.Char(string='CTA Button Label')
    cta_url = fields.Char(string='CTA URL')
    image_url = fields.Char(string='Image URL')
    company_id = fields.Many2one(
        related='page_id.company_id',
        store=True,
        index=True,
    )

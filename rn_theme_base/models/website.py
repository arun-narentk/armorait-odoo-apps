from odoo import fields, models
import json


class Website(models.Model):
    _inherit = 'website'

    tb_primary_color = fields.Char(
        string='Theme Primary Color',
        default='#1a3a5c',
        help='Primary brand color applied as a CSS variable on the frontend.',
    )
    tb_secondary_color = fields.Char(
        string='Theme Secondary Color',
        default='#2d7dd2',
        help='Secondary brand color applied as a CSS variable on the frontend.',
    )
    tb_accent_color = fields.Char(
        string='Theme Accent Color',
        default='#f4a261',
        help='Accent color for highlights and call-to-action elements.',
    )
    tb_heading_font = fields.Char(
        string='Heading Font',
        default='Poppins',
        help='Google Font family name for headings.',
    )
    tb_body_font = fields.Char(
        string='Body Font',
        default='Inter',
        help='Google Font family name for body text.',
    )
    tb_enable_animations = fields.Boolean(
        string='Enable Scroll Animations',
        default=True,
    )
    tb_sticky_header = fields.Boolean(
        string='Sticky Header',
        default=True,
    )
    tb_whatsapp_number = fields.Char(
        string='WhatsApp Number',
        help='International format without plus sign, e.g. 919876543210.',
    )
    tb_show_emergency_banner = fields.Boolean(
        string='Show Emergency Banner',
        default=False,
    )
    tb_emergency_banner_text = fields.Char(
        string='Emergency Banner Text',
        default='Important notice for all visitors.',
    )

    def _tb_get_organization_schema(self):
        self.ensure_one()
        base_url = self.domain or ''
        return json.dumps({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            'name': self.name,
            'url': base_url,
            'logo': self.image_url(self, 'logo'),
        })

    def _tb_get_customizer_values(self):
        self.ensure_one()
        return {
            'primary_color': self.tb_primary_color or '#1a3a5c',
            'secondary_color': self.tb_secondary_color or '#2d7dd2',
            'accent_color': self.tb_accent_color or '#f4a261',
            'heading_font': self.tb_heading_font or 'Poppins',
            'body_font': self.tb_body_font or 'Inter',
            'enable_animations': self.tb_enable_animations,
            'sticky_header': self.tb_sticky_header,
            'whatsapp_number': self.tb_whatsapp_number or '',
            'show_emergency_banner': self.tb_show_emergency_banner,
            'emergency_banner_text': self.tb_emergency_banner_text or '',
        }

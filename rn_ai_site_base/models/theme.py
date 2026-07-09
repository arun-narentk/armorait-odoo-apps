# -*- coding: utf-8 -*-
"""Theme presets."""

from odoo import fields, models


class RnAiSiteTheme(models.Model):
    """Reusable color and font theme preset."""

    _name = 'rn.ai.site.theme'
    _description = 'AI Site Theme Preset'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    primary_color = fields.Char(default='#2563eb')
    secondary_color = fields.Char(default='#1e293b')
    accent_color = fields.Char(default='#f59e0b')
    background_color = fields.Char(default='#ffffff')
    font_heading = fields.Char(default='Inter')
    font_body = fields.Char(default='Inter')
    layout_style = fields.Selection(
        selection=[
            ('modern', 'Modern'),
            ('classic', 'Classic'),
            ('minimal', 'Minimal'),
            ('bold', 'Bold'),
        ],
        default='modern',
    )
    business_types = fields.Char(
        help='Comma-separated business types this theme suits best',
    )

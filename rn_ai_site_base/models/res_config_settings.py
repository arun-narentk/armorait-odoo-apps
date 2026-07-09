# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_site_default_language = fields.Selection(
        related='company_id.ai_site_default_language',
        readonly=False,
    )
    ai_site_enable_llm = fields.Boolean(
        related='company_id.ai_site_enable_llm',
        readonly=False,
    )
    ai_site_enable_auto_crm = fields.Boolean(
        related='company_id.ai_site_enable_auto_crm',
        readonly=False,
    )
    ai_site_publisher_mode = fields.Selection(
        related='company_id.ai_site_publisher_mode',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    ai_site_default_language = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
        ],
        default='en',
    )
    ai_site_enable_llm = fields.Boolean(default=False)
    ai_site_enable_auto_crm = fields.Boolean(default=True)
    ai_site_publisher_mode = fields.Selection(
        selection=[
            ('odoo', 'Odoo Website'),
            ('standalone', 'Standalone Hosting'),
            ('both', 'Both'),
        ],
        default='odoo',
    )

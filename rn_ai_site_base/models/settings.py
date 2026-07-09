# -*- coding: utf-8 -*-
"""AI site builder settings."""

from odoo import fields, models


class RnAiSiteSettings(models.Model):
    """Defaults for AI Business Launch platform."""

    _name = 'rn.ai.site.settings'
    _description = 'AI Site Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='AI Site Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_language = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
        ],
        default='en',
    )
    enable_llm_content = fields.Boolean(
        default=False,
        string='Use LLM for Content',
        help='When enabled, companion rn_ai_site_content module can call external AI APIs.',
    )
    enable_auto_crm = fields.Boolean(default=True, string='Auto-create CRM on Publish')
    enable_auto_seo = fields.Boolean(default=True)
    max_sites = fields.Integer(default=10, string='Max Sites per Company')
    credit_balance = fields.Integer(default=100, string='AI Credits Remaining')
    publisher_mode = fields.Selection(
        selection=[
            ('odoo', 'Odoo Website'),
            ('standalone', 'Standalone Hosting'),
            ('both', 'Both'),
        ],
        default='odoo',
    )
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one AI site settings record per company.',
    )

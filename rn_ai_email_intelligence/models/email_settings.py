# -*- coding: utf-8 -*-
"""AI email platform settings and credits."""

from odoo import fields, models


class RnAiEmailSettings(models.Model):
    _name = 'rn.ai.email.settings'
    _description = 'AI Email Settings'
    _inherit = ['mail.thread']

    name = fields.Char(default='AI Email Settings', required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    monthly_credit_limit = fields.Integer(default=500)
    credit_balance = fields.Integer(default=500)
    default_tone = fields.Selection(
        selection=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('formal', 'Formal'),
        ],
        default='professional',
    )
    default_language = fields.Selection(
        selection=[('en', 'English'), ('ta', 'Tamil'), ('hi', 'Hindi')],
        default='en',
    )
    enable_llm_provider = fields.Boolean(
        default=False,
        help='Use external LLM when API key is configured.',
    )
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one AI email settings record per company.',
    )

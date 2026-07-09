# -*- coding: utf-8 -*-
"""Company settings for AI document automation."""

from odoo import fields, models


class RnAiDocumentSettings(models.Model):
    _name = 'rn.ai.document.settings'
    _description = 'AI Document Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    ai_provider = fields.Selection(
        selection=[
            ('builtin', 'Built-in Draft Engine'),
            ('openai', 'OpenAI Compatible'),
            ('disabled', 'Disabled (Templates Only)'),
        ],
        default='builtin',
        required=True,
    )
    ai_api_url = fields.Char(string='AI API URL')
    ai_api_key = fields.Char(string='AI API Key', groups='rn_ai_document_generator.group_rn_ai_doc_manager')
    ai_model = fields.Char(default='gpt-4o-mini')
    default_language = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
            ('ar', 'Arabic'),
            ('fr', 'French'),
            ('de', 'German'),
        ],
        default='en',
    )
    default_style = fields.Selection(
        selection=[
            ('formal', 'Formal'),
            ('corporate', 'Corporate'),
            ('legal', 'Legal'),
            ('friendly', 'Friendly'),
            ('executive', 'Executive'),
            ('technical', 'Technical'),
            ('marketing', 'Marketing'),
        ],
        default='formal',
    )
    auto_snapshot = fields.Boolean(default=True)
    enable_watermark = fields.Boolean(default=False)
    watermark_text = fields.Char(default='DRAFT')

    _rn_ai_document_settings_company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one settings row per company.',
    )

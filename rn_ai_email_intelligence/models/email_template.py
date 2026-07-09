# -*- coding: utf-8 -*-
"""Reusable AI email templates by business category."""

from odoo import fields, models


class RnAiEmailTemplate(models.Model):
    _name = 'rn.ai.email.template'
    _description = 'AI Email Template'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    category = fields.Selection(
        selection=[
            ('sales', 'Sales'),
            ('accounting', 'Accounting'),
            ('crm', 'CRM'),
            ('helpdesk', 'Helpdesk'),
            ('hr', 'HR'),
            ('purchase', 'Purchase'),
            ('general', 'General'),
        ],
        default='sales',
        required=True,
    )
    prompt_hint = fields.Text(
        help='Instructions used when generating drafts from this template.',
    )
    subject_pattern = fields.Char(help='e.g. Follow-up on quotation {{quotation}}')
    body_pattern = fields.Html()
    default_tone = fields.Selection(
        selection=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('formal', 'Formal'),
            ('persuasive', 'Persuasive'),
            ('apologetic', 'Apologetic'),
            ('concise', 'Concise'),
        ],
        default='professional',
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _template_code_company_uniq = models.Constraint(
        'unique(code, company_id)',
        'Template code must be unique per company.',
    )

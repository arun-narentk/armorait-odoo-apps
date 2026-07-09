# -*- coding: utf-8 -*-
"""Document type catalog (sales, HR, legal, etc.)."""

from odoo import fields, models


class RnAiDocumentType(models.Model):
    """Classification for templates and generated documents."""

    _name = 'rn.ai.document.type'
    _description = 'AI Document Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    category = fields.Selection(
        selection=[
            ('sales', 'Sales'),
            ('purchase', 'Purchase'),
            ('hr', 'HR'),
            ('legal', 'Legal'),
            ('finance', 'Finance'),
            ('admin', 'Administration'),
            ('custom', 'Custom'),
        ],
        required=True,
        default='custom',
        index=True,
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
    require_approval = fields.Boolean(default=False)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _rn_ai_document_type_code_uniq = models.Constraint(
        'unique(code, company_id)',
        'Document type code must be unique per company.',
    )

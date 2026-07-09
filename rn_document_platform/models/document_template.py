# -*- coding: utf-8 -*-
"""Reusable document templates for signing."""

from odoo import fields, models


class RnDocPlatformTemplate(models.Model):
    """Template for documents sent for signature."""

    _name = 'rn.doc.platform.template'
    _description = 'Document Platform Template'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    category = fields.Selection(
        selection=[
            ('sales', 'Sales'),
            ('purchase', 'Purchase'),
            ('hr', 'HR'),
            ('accounting', 'Accounting'),
            ('legal', 'Legal'),
            ('other', 'Other'),
        ],
        default='sales',
        required=True,
    )
    model_id = fields.Many2one('ir.model', string='Source Model')
    body_html = fields.Html()
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

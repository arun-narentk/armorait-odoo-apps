# -*- coding: utf-8 -*-
"""Reusable HTML / placeholder templates."""

from odoo import api, fields, models


class RnAiDocumentTemplate(models.Model):
    """Template with placeholders and optional AI sections."""

    _name = 'rn.ai.document.template'
    _description = 'AI Document Template'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    type_id = fields.Many2one('rn.ai.document.type', required=True, index=True)
    language = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
            ('ar', 'Arabic'),
            ('fr', 'French'),
            ('de', 'German'),
        ],
        default='en',
        required=True,
    )
    style = fields.Selection(
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
        required=True,
    )
    body_html = fields.Html(string='Template Body', sanitize=False)
    placeholder_help = fields.Text(
        string='Placeholder Reference',
        default='{{customer_name}} {{employee_name}} {{company_name}} {{invoice_total}} {{joining_date}} {{salary}} {{quotation_items}} {{valid_until}}',
    )
    ai_prompt = fields.Text(
        string='AI Prompt Hint',
        help='Extra instructions for AI-generated clauses (scope, terms, intro, etc.).',
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Source Model',
        ondelete='set null',
        help='Optional Odoo model used to resolve dynamic variables.',
    )
    model_name = fields.Char(related='model_id.model', store=True, index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.ai.document.template') or 'New'
        return super().create(vals_list)

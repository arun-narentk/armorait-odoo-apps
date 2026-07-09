# -*- coding: utf-8 -*-
"""AI contract analysis results."""

from odoo import fields, models


class RnDocAiAnalysis(models.Model):
    """AI summary and risk analysis for a document."""

    _name = 'rn.doc.ai.analysis'
    _description = 'Document AI Analysis'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True)
    request_id = fields.Many2one('rn.doc.sign.request', index=True)
    summary_html = fields.Html()
    contract_value = fields.Char()
    duration = fields.Char()
    renewal_date = fields.Date()
    notice_period = fields.Char()
    payment_terms = fields.Char()
    risk_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='low',
    )
    risk_flags = fields.Text(help='One risk per line')
    clause_highlights = fields.Html()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

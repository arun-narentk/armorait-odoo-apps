# -*- coding: utf-8 -*-
"""AI-generated factory insights."""

from odoo import fields, models


class RnMrpAiInsight(models.Model):
    """Stored AI or heuristic factory summary."""

    _name = 'rn.mrp.ai.insight'
    _description = 'Manufacturing AI Insight'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True)
    insight_type = fields.Selection(
        selection=[
            ('daily_summary', 'Daily Factory Summary'),
            ('bottleneck', 'Bottleneck Alert'),
            ('forecast', 'Production Forecast'),
            ('scrap', 'Scrap Analysis'),
            ('maintenance', 'Maintenance Prediction'),
        ],
        default='daily_summary',
        required=True,
    )
    summary_html = fields.Html(required=True)
    severity = fields.Selection(
        selection=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ],
        default='info',
    )
    date = fields.Date(default=fields.Date.context_today)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

# -*- coding: utf-8 -*-
"""AI workforce insight records."""

from odoo import fields, models


class RnHrAiInsight(models.Model):
    """Stored workforce intelligence narrative."""

    _name = 'rn.hr.ai.insight'
    _description = 'HR AI Insight'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True)
    insight_type = fields.Selection(
        selection=[
            ('payroll_summary', 'Payroll Summary'),
            ('overtime', 'Overtime Alert'),
            ('attrition', 'Attrition Trend'),
            ('forecast', 'Salary Forecast'),
            ('anomaly', 'Anomaly Detection'),
            ('optimization', 'Cost Optimization'),
        ],
        default='payroll_summary',
        required=True,
    )
    summary_html = fields.Html(required=True)
    severity = fields.Selection(
        selection=[('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical')],
        default='info',
    )
    period = fields.Date()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

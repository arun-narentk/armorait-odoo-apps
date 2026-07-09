# -*- coding: utf-8 -*-
"""AI-ready prediction records for CRM leads."""

from odoo import fields, models


class RnCrmPrediction(models.Model):
    """Stores prediction outputs from a pluggable prediction provider."""

    _name = 'rn.crm.prediction'
    _description = 'CRM Lead Prediction'
    _order = 'create_date desc'

    lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade', index=True)
    win_probability = fields.Float(digits=(16, 2))
    expected_close_date = fields.Date()
    revenue_confidence = fields.Float(digits=(16, 2))
    recommended_activity = fields.Char()
    risk_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        default='medium',
    )
    provider = fields.Char(default='rule_engine', help='Prediction provider key.')
    payload = fields.Text(help='JSON debug payload from provider.')
    company_id = fields.Many2one(related='lead_id.company_id', store=True)

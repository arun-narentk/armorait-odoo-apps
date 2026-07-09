# -*- coding: utf-8 -*-
"""Company manufacturing intelligence settings."""

from odoo import fields, models


class RnMrpIntelligenceSettings(models.Model):
    """Per-company MRP intelligence configuration."""

    _name = 'rn.mrp.intelligence.settings'
    _description = 'Manufacturing Intelligence Settings'
    _inherit = ['mail.thread']

    name = fields.Char(default='Manufacturing Intelligence Settings', required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    enable_ai_summary = fields.Boolean(default=True, string='AI Factory Summary')
    enable_bottleneck_detection = fields.Boolean(default=True)
    oee_target = fields.Float(default=75.0, string='OEE Target %')
    low_stock_days = fields.Integer(default=3, string='Low Stock Warning (days)')
    dashboard_refresh_seconds = fields.Integer(default=60)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one intelligence settings record per company.',
    )

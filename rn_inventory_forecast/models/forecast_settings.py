# -*- coding: utf-8 -*-
"""Company-level forecast settings."""

from odoo import fields, models


class RnInvForecastSettings(models.Model):
    """Defaults for forecasting and planning."""

    _name = 'rn.inv.forecast.settings'
    _description = 'Inventory Forecast Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Inventory Forecast Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_horizon_days = fields.Integer(default=30)
    default_lead_time_days = fields.Integer(default=7)
    service_level = fields.Float(default=0.95, digits=(16, 4))
    history_days = fields.Integer(default=90)
    dead_stock_days = fields.Integer(default=90, help='No movement after N days marks dead stock.')
    low_stock_coverage_days = fields.Float(default=7.0)
    overstock_coverage_days = fields.Float(default=90.0)
    abc_a_pct = fields.Float(default=80.0, help='Cumulative value share for class A.')
    abc_b_pct = fields.Float(default=95.0)
    enable_alerts = fields.Boolean(default=True)
    enable_auto_forecast = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one inventory forecast settings record per company.',
    )

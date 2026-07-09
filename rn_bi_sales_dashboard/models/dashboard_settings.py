# -*- coding: utf-8 -*-
"""Company BI dashboard settings."""

from odoo import fields, models


class RnBiDashboardSettings(models.Model):
    """Theme, refresh, and display defaults for BI Sales."""

    _name = 'rn.bi.dashboard.settings'
    _description = 'BI Dashboard Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='BI Sales Settings')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    theme = fields.Selection(
        selection=[('light', 'Light'), ('dark', 'Dark'), ('corporate', 'Corporate')],
        default='light',
    )
    refresh_interval = fields.Integer(default=300)
    chart_color_primary = fields.Char(default='#4F46E5')
    chart_color_secondary = fields.Char(default='#22C55E')
    decimal_precision = fields.Integer(default=2)
    timezone = fields.Char(default='UTC')
    cache_ttl_seconds = fields.Integer(default=120)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one BI dashboard settings record per company.',
    )

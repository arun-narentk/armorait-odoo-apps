# -*- coding: utf-8 -*-
"""Company-level dashboard engine settings."""

from odoo import fields, models


class RnDashboardSettings(models.Model):
    """Defaults for refresh, cache, and TV boards."""

    _name = 'rn.dashboard.settings'
    _description = 'Dashboard Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    default_refresh_seconds = fields.Integer(default=30)
    tv_refresh_seconds = fields.Integer(default=10)
    cache_ttl_seconds = fields.Integer(default=60)
    enable_alerts = fields.Boolean(default=True)
    enable_public_tv = fields.Boolean(
        string='Enable Public TV Token Routes',
        default=False,
        help='Future kiosk routes. Keep off until rn_mrp_production_tv is installed.',
    )
    retention_days = fields.Integer(
        string='Snapshot Retention (days)',
        default=90,
    )

    _rn_dashboard_settings_company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one settings row per company.',
    )

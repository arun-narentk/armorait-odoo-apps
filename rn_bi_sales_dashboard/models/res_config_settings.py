# -*- coding: utf-8 -*-
"""Settings app bridge for BI Sales Dashboard."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose BI Sales toggles."""

    _inherit = 'res.config.settings'

    rn_bi_sales_enabled = fields.Boolean(
        string='Enable BI Sales Dashboard',
        config_parameter='rn_bi_sales_dashboard.enabled',
        default=True,
    )
    rn_bi_sales_refresh = fields.Integer(
        string='Default Refresh Interval (seconds)',
        config_parameter='rn_bi_sales_dashboard.refresh_interval',
        default=300,
    )
    rn_bi_sales_cache_ttl = fields.Integer(
        string='Cache TTL (seconds)',
        config_parameter='rn_bi_sales_dashboard.cache_ttl',
        default=120,
    )

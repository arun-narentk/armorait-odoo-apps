# -*- coding: utf-8 -*-
"""Settings app bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose inventory forecast toggles."""

    _inherit = 'res.config.settings'

    rn_inv_forecast_enabled = fields.Boolean(
        string='Enable Inventory Forecast',
        config_parameter='rn_inventory_forecast.enabled',
        default=True,
    )
    rn_inv_forecast_horizon = fields.Integer(
        string='Default Horizon (days)',
        config_parameter='rn_inventory_forecast.horizon_days',
        default=30,
    )
    rn_inv_forecast_history = fields.Integer(
        string='History Window (days)',
        config_parameter='rn_inventory_forecast.history_days',
        default=90,
    )

# -*- coding: utf-8 -*-
"""Settings app bridge for ARMORA Rental."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose rental core toggles."""

    _inherit = 'res.config.settings'

    rn_rental_enabled = fields.Boolean(
        string='Enable ARMORA Rental Core',
        config_parameter='rn_rental_core.enabled',
        default=True,
    )
    rn_rental_default_plan = fields.Selection(
        selection=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        string='Default Rental Plan',
        config_parameter='rn_rental_core.default_plan',
        default='daily',
    )

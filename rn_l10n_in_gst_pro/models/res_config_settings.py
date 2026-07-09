# -*- coding: utf-8 -*-
"""System settings bridge for GST Pro."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose GST Pro toggles on Settings."""

    _inherit = 'res.config.settings'

    rn_gst_enabled = fields.Boolean(
        string='Enable GST Compliance Pro',
        config_parameter='rn_l10n_in_gst_pro.enabled',
    )
    rn_gst_json_version = fields.Char(
        string='GST JSON Version',
        config_parameter='rn_l10n_in_gst_pro.json_version',
        default='GST3.1.6',
    )
    rn_gst_auto_validate = fields.Boolean(
        string='Auto Validate Returns',
        config_parameter='rn_l10n_in_gst_pro.auto_validate',
        default=True,
    )
    rn_gst_return_frequency = fields.Selection(
        selection=[
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
        ],
        string='Default Return Frequency',
        config_parameter='rn_l10n_in_gst_pro.return_frequency',
        default='month',
    )

# -*- coding: utf-8 -*-
"""Settings app bridge for Hospital ERP."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose HMS Core toggles."""

    _inherit = 'res.config.settings'

    rn_hms_enabled = fields.Boolean(
        string='Enable ARMORA Hospital ERP',
        config_parameter='rn_hms_core.enabled',
        default=True,
    )
    rn_hms_patient_prefix = fields.Char(
        string='Patient Code Prefix',
        config_parameter='rn_hms_core.patient_code_prefix',
        default='P',
    )

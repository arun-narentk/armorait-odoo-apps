# -*- coding: utf-8 -*-
"""Settings app bridge for ARMORA HRMS."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose HRMS Core toggles."""

    _inherit = 'res.config.settings'

    rn_hrms_enabled = fields.Boolean(
        string='Enable ARMORA HRMS Core',
        config_parameter='rn_hrms_core.enabled',
        default=True,
    )
    rn_hrms_code_prefix = fields.Char(
        string='Employee Code Prefix',
        config_parameter='rn_hrms_core.employee_code_prefix',
        default='EMP',
    )

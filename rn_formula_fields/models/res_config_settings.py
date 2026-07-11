# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_formula_allow_stored = fields.Boolean(
        string='Allow Stored Formula Fields',
        config_parameter='rn_formula_fields.allow_stored',
        default=True,
    )
    rn_formula_log_errors = fields.Boolean(
        string='Log Formula Evaluation Errors',
        config_parameter='rn_formula_fields.log_errors',
        default=True,
    )

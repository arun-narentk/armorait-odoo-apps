# -*- coding: utf-8 -*-
"""Settings app bridge for CRM Ultimate Pro."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose CRM Ultimate Pro toggles."""

    _inherit = 'res.config.settings'

    rn_crm_scoring_enabled = fields.Boolean(
        string='Enable Lead Scoring',
        config_parameter='rn_crm_ultimate_pro.scoring_enabled',
        default=True,
    )
    rn_crm_duplicate_sensitivity = fields.Selection(
        selection=[('strict', 'Strict'), ('balanced', 'Balanced'), ('loose', 'Loose')],
        string='Duplicate Sensitivity',
        config_parameter='rn_crm_ultimate_pro.duplicate_sensitivity',
        default='balanced',
    )
    rn_crm_prediction_provider = fields.Selection(
        selection=[
            ('rule_engine', 'Rule Engine'),
            ('external', 'External AI Provider'),
        ],
        string='Prediction Provider',
        config_parameter='rn_crm_ultimate_pro.prediction_provider',
        default='rule_engine',
    )
    rn_crm_round_robin = fields.Boolean(
        string='Round Robin Assignment',
        config_parameter='rn_crm_ultimate_pro.round_robin',
    )

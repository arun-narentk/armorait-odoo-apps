# -*- coding: utf-8 -*-
"""Settings extension for AI Employee."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_ai_employee_enabled = fields.Boolean(
        string='Enable AI Employee',
        config_parameter='rn_ai_employee.enabled',
    )
    rn_ai_employee_provider = fields.Selection(
        selection=[
            ('openai', 'OpenAI'),
        ],
        string='AI Provider',
        config_parameter='rn_ai_employee.provider',
        default='openai',
    )
    rn_ai_employee_api_key = fields.Char(
        string='API Key',
        config_parameter='rn_ai_employee.api_key',
    )
    rn_ai_employee_api_url = fields.Char(
        string='API URL',
        config_parameter='rn_ai_employee.api_url',
        default='https://api.openai.com/v1/chat/completions',
    )
    rn_ai_employee_model = fields.Char(
        string='Model Name',
        config_parameter='rn_ai_employee.model',
        default='gpt-4o-mini',
    )
    rn_ai_employee_temperature = fields.Float(
        string='Temperature',
        config_parameter='rn_ai_employee.temperature',
        default=0.2,
    )

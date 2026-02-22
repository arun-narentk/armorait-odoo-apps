# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_resume_ai_parser_auto_create_skills = fields.Boolean(
        string='Auto-create skills from resume',
        config_parameter='hr_resume_ai_parser.auto_create_skills',
        help='When parsing resumes, create new hr.skill records for unknown skills instead of skipping them.',
    )

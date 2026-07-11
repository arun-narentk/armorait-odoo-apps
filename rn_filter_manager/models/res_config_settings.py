# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_filter_recent_limit = fields.Integer(
        string='Maximum Recent Filters',
        default=50,
        config_parameter='rn_filter_manager.recent_limit',
    )
    rn_filter_remember_searches = fields.Boolean(
        string='Remember Searches',
        default=True,
        config_parameter='rn_filter_manager.remember_searches',
    )
    rn_filter_enable_teams = fields.Boolean(
        string='Enable Team Folders',
        default=True,
        config_parameter='rn_filter_manager.enable_teams',
    )
    rn_filter_enable_folders = fields.Boolean(
        string='Enable Folders',
        default=True,
        config_parameter='rn_filter_manager.enable_folders',
    )
    rn_filter_duplicate_detection = fields.Boolean(
        string='Duplicate Detection',
        default=True,
        config_parameter='rn_filter_manager.duplicate_detection',
    )

# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_bookmark_recent_limit = fields.Integer(
        string='Recent Bookmark Limit',
        default=50,
        config_parameter='rn_bookmarks.recent_limit',
    )
    rn_bookmark_enable_hotkey = fields.Boolean(
        string='Enable Ctrl+B Hotkey',
        default=True,
        config_parameter='rn_bookmarks.enable_hotkey',
    )
    rn_bookmark_enable_systray = fields.Boolean(
        string='Show Sidebar Systray',
        default=True,
        config_parameter='rn_bookmarks.enable_systray',
    )

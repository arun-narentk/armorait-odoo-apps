# -*- coding: utf-8 -*-

from odoo import fields, models

from odoo.addons.rn_smart_search.constants import (
    DEFAULT_AUTO_CLEAN_DAYS,
    DEFAULT_MAX_HISTORY,
    DEFAULT_REMEMBER_SEARCHES,
    DEFAULT_REMEMBER_VIEWED,
    PARAM_AUTO_CLEAN_DAYS,
    PARAM_MAX_HISTORY,
    PARAM_REMEMBER_SEARCHES,
    PARAM_REMEMBER_VIEWED,
)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_smart_search_remember_viewed = fields.Boolean(
        string='Remember viewed records',
        config_parameter=PARAM_REMEMBER_VIEWED,
        default=DEFAULT_REMEMBER_VIEWED,
    )
    rn_smart_search_remember_searches = fields.Boolean(
        string='Remember search queries',
        config_parameter=PARAM_REMEMBER_SEARCHES,
        default=DEFAULT_REMEMBER_SEARCHES,
    )
    rn_smart_search_max_history = fields.Integer(
        string='Maximum history entries',
        config_parameter=PARAM_MAX_HISTORY,
        default=DEFAULT_MAX_HISTORY,
    )
    rn_smart_search_auto_clean_days = fields.Integer(
        string='Auto-clean after (days)',
        config_parameter=PARAM_AUTO_CLEAN_DAYS,
        default=DEFAULT_AUTO_CLEAN_DAYS,
    )

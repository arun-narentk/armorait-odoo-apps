# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_timeline_auto_log = fields.Boolean(
        string='Auto-log timeline events',
        config_parameter='rn_record_timeline.auto_log',
        default=True,
    )
    rn_timeline_default_limit = fields.Integer(
        string='Timeline page size',
        config_parameter='rn_record_timeline.default_limit',
        default=50,
    )

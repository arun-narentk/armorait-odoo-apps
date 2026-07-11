# -*- coding: utf-8 -*-

from odoo import fields, models

from odoo.addons.rn_record_share import constants as const


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_record_share_default_format = fields.Selection(
        selection=const.COPY_FORMATS,
        string='Default Copy Format',
        config_parameter='rn_record_share.default_format',
        default=const.DEFAULT_LINK_FORMAT,
    )
    rn_record_share_log_retention_days = fields.Integer(
        string='Share Log Retention (Days)',
        config_parameter='rn_record_share.log_retention_days',
        default=const.DEFAULT_LOG_RETENTION_DAYS,
    )
    rn_record_share_enable_whatsapp = fields.Boolean(
        string='Enable WhatsApp Share',
        config_parameter='rn_record_share.enable_whatsapp',
        default=True,
    )
    rn_record_share_enable_email = fields.Boolean(
        string='Enable Email Share',
        config_parameter='rn_record_share.enable_email',
        default=True,
    )

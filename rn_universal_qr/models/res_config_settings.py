# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_qr_default_template_id = fields.Many2one(
        'rn.qr.template',
        string='Default QR Template',
        config_parameter='rn_universal_qr.default_template_id',
    )
    rn_qr_default_expiration_days = fields.Integer(
        string='Default Expiration Days',
        default=0,
        config_parameter='rn_universal_qr.default_expiration_days',
    )
    rn_qr_default_scan_action = fields.Selection(
        [('open_record', 'Open Record'), ('portal_page', 'Open Portal Page')],
        default='open_record',
        config_parameter='rn_universal_qr.default_scan_action',
    )

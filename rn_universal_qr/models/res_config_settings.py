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
        [('open_form', 'Open Form'), ('redirect_portal', 'Portal Redirect')],
        default='open_form',
        config_parameter='rn_universal_qr.default_scan_action',
    )
# -*- coding: utf-8 -*-

from odoo import api, fields, models

from odoo.addons.rn_universal_qr import constants


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_qr_default_size = fields.Selection(
        selection=constants.QR_SIZES,
        string='Default QR Size',
        default=constants.DEFAULT_QR_SIZE,
        config_parameter='rn_universal_qr.default_size',
    )
    rn_qr_default_color = fields.Selection(
        selection=constants.QR_COLORS,
        string='Default QR Color',
        default=constants.DEFAULT_QR_COLOR,
        config_parameter='rn_universal_qr.default_color',
    )
    rn_qr_custom_color = fields.Char(
        string='Custom QR Color',
        default='#000000',
        config_parameter='rn_universal_qr.custom_color',
    )
    rn_qr_ecc_level = fields.Selection(
        selection=constants.QR_ECC_LEVELS,
        string='ECC Level',
        default=constants.DEFAULT_ECC_LEVEL,
        config_parameter='rn_universal_qr.ecc_level',
    )
    rn_qr_use_logo = fields.Boolean(
        string='Logo in Center',
        config_parameter='rn_universal_qr.use_logo',
    )
    rn_qr_payload_type = fields.Selection(
        selection=constants.QR_PAYLOAD_TYPES,
        string='Default Payload',
        default=constants.DEFAULT_PAYLOAD_TYPE,
        config_parameter='rn_universal_qr.payload_type',
    )
    rn_qr_action_type = fields.Selection(
        selection=constants.QR_ACTION_TYPES,
        string='Default Action',
        default=constants.DEFAULT_ACTION_TYPE,
        config_parameter='rn_universal_qr.action_type',
    )
    rn_qr_expiration_policy = fields.Selection(
        selection=constants.QR_EXPIRATION,
        string='Default Expiration',
        default='never',
        config_parameter='rn_universal_qr.expiration_policy',
    )
    rn_qr_enable_statistics = fields.Boolean(
        string='Enable Scan Statistics',
        default=True,
        config_parameter='rn_universal_qr.enable_statistics',
    )
    rn_qr_enable_public_url = fields.Boolean(
        string='Enable Public URL Payload',
        default=True,
        config_parameter='rn_universal_qr.enable_public_url',
    )
    rn_qr_enable_report = fields.Boolean(
        string='Enable QR on Reports',
        default=True,
        config_parameter='rn_universal_qr.enable_report',
    )

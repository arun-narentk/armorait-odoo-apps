# -*- coding: utf-8 -*-
"""System settings for WhatsApp Connector."""

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Expose WhatsApp Connector settings on the general settings page."""

    _inherit = 'res.config.settings'

    rn_whatsapp_enabled = fields.Boolean(
        string='Enable WhatsApp Connector',
        config_parameter='rn_whatsapp_connector.enabled',
    )
    rn_whatsapp_default_account_id = fields.Many2one(
        'rn.whatsapp.account',
        string='Default WhatsApp Account',
    )
    rn_whatsapp_timeout = fields.Integer(
        string='API Timeout (seconds)',
        config_parameter='rn_whatsapp_connector.timeout',
        default=30,
    )
    rn_whatsapp_max_retries = fields.Integer(
        string='Max Retries',
        config_parameter='rn_whatsapp_connector.max_retries',
        default=3,
    )
    rn_whatsapp_debug_mode = fields.Boolean(
        string='Debug Mode',
        config_parameter='rn_whatsapp_connector.debug_mode',
    )
    rn_whatsapp_rate_limit = fields.Integer(
        string='Rate Limit (messages/minute)',
        config_parameter='rn_whatsapp_connector.rate_limit',
        default=60,
    )
    rn_whatsapp_max_attachment_mb = fields.Integer(
        string='Maximum Attachment Size (MB)',
        config_parameter='rn_whatsapp_connector.max_attachment_mb',
        default=16,
    )
    rn_whatsapp_allowed_extensions = fields.Char(
        string='Allowed Extensions',
        config_parameter='rn_whatsapp_connector.allowed_extensions',
        default='pdf,png,jpg,jpeg,mp4,doc,docx',
    )

    @api.model
    def get_values(self):
        """Load default account from config parameter."""
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo().get_param(
            'rn_whatsapp_connector.default_account_id'
        )
        res['rn_whatsapp_default_account_id'] = int(param) if param else False
        return res

    def set_values(self):
        """Persist default account to config parameter."""
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'rn_whatsapp_connector.default_account_id',
            str(self.rn_whatsapp_default_account_id.id or ''),
        )

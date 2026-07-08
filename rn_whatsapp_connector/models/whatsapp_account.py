# -*- coding: utf-8 -*-
"""WhatsApp account model."""

from odoo import api, fields, models


class RnWhatsappAccount(models.Model):
    """Stores connection credentials and health for a WhatsApp provider account."""

    _name = 'rn.whatsapp.account'
    _description = 'WhatsApp Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    provider = fields.Selection(
        selection=[
            ('meta_cloud', 'Meta Cloud API'),
            ('chat_api', 'Chat API'),
            ('twilio', 'Twilio'),
            ('dialog360', '360Dialog'),
            ('ultramsg', 'UltraMsg'),
            ('green_api', 'Green API'),
        ],
        required=True,
        default='meta_cloud',
        tracking=True,
    )
    phone_number = fields.Char(string='Phone Number', tracking=True)
    business_id = fields.Char(string='Business ID')
    api_url = fields.Char(string='API URL')
    api_version = fields.Char(string='API Version', default='v21.0')
    access_token = fields.Char(string='Access Token', groups='rn_whatsapp_connector.group_rn_whatsapp_admin')
    webhook_token = fields.Char(string='Webhook Token', groups='rn_whatsapp_connector.group_rn_whatsapp_admin')
    webhook_verify_token = fields.Char(
        string='Webhook Verify Token',
        groups='rn_whatsapp_connector.group_rn_whatsapp_admin',
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('connected', 'Connected'),
            ('disconnected', 'Disconnected'),
            ('error', 'Error'),
        ],
        default='draft',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    last_sync = fields.Datetime(string='Last Sync')
    profile_picture = fields.Binary(string='Profile Picture', attachment=True)
    phone_quality_rating = fields.Selection(
        selection=[
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('red', 'Red'),
            ('unknown', 'Unknown'),
        ],
        default='unknown',
    )
    daily_limit = fields.Integer(string='Daily Limit', default=1000)
    messages_today = fields.Integer(string='Messages Today', default=0)
    connection_state = fields.Selection(
        selection=[
            ('offline', 'Offline'),
            ('online', 'Online'),
            ('pairing', 'Pairing'),
        ],
        default='offline',
    )
    qr_code = fields.Binary(string='QR Code', attachment=True)
    message_ids = fields.One2many('rn.whatsapp.message', 'account_id', string='Messages')
    template_ids = fields.One2many('rn.whatsapp.template', 'account_id', string='Templates')
    message_count = fields.Integer(compute='_compute_message_count')

    @api.depends('message_ids')
    def _compute_message_count(self):
        """Count linked messages for list view smart buttons."""
        for account in self:
            account.message_count = len(account.message_ids)

    def action_test_connection(self):
        """Trigger a provider health check via the provider service (Phase 3)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'WhatsApp Connector',
                'message': 'Connection test will be available in the provider layer (Phase 3).',
                'type': 'info',
                'sticky': False,
            },
        }

    def action_view_messages(self):
        """Open messages linked to this account."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Messages',
            'res_model': 'rn.whatsapp.message',
            'view_mode': 'list,form',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id},
        }

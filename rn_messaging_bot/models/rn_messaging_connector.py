# -*- coding: utf-8 -*-
"""Messaging channel connector configuration."""

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RnMessagingConnector(models.Model):
    _name = 'rn.messaging.connector'
    _description = 'Messaging Connector'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    channel_type = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('instagram', 'Instagram DM'),
            ('facebook', 'Facebook Messenger'),
            ('livechat', 'Website Live Chat'),
        ],
        required=True,
        default='whatsapp',
        tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    bot_id = fields.Many2one(
        'rn.messaging.bot',
        string='Default Bot',
        domain="[('company_id', 'in', (company_id, False))]",
    )
    simulation_mode = fields.Boolean(
        string='Simulation Mode',
        default=True,
        help='Log outbound messages without calling external APIs.',
    )
    phone_number = fields.Char(string='Display Phone / Page ID')
    api_url = fields.Char(string='API URL', default='https://graph.facebook.com')
    api_version = fields.Char(default='v21.0')
    access_token = fields.Char(groups='rn_messaging_bot.group_rn_messaging_admin')
    webhook_verify_token = fields.Char(groups='rn_messaging_bot.group_rn_messaging_admin')
    webhook_secret = fields.Char(groups='rn_messaging_bot.group_rn_messaging_admin')
    phone_number_id = fields.Char(string='WhatsApp Phone Number ID')
    page_id = fields.Char(string='Facebook Page ID')
    instagram_account_id = fields.Char(string='Instagram Account ID')
    business_account_id = fields.Char(string='Business Account ID')
    linked_account_ref = fields.Reference(
        selection='_selection_linked_accounts',
        string='Linked WhatsApp Account',
        help='Optional link to rn_whatsapp_connector when that module is installed.',
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('connected', 'Connected'),
            ('error', 'Error'),
        ],
        default='draft',
        tracking=True,
    )
    conversation_count = fields.Integer(compute='_compute_conversation_count')
    webhook_path = fields.Char(compute='_compute_webhook_path', string='Webhook URL Path')

    @api.depends('channel_type')
    def _compute_webhook_path(self):
        for connector in self:
            connector.webhook_path = f'/rn_messaging/webhook/{connector.id}'

    def _compute_conversation_count(self):
        grouped = self.env['rn.messaging.conversation'].read_group(
            [('connector_id', 'in', self.ids)],
            ['connector_id'],
            ['connector_id'],
        )
        counts = {row['connector_id'][0]: row['connector_id_count'] for row in grouped}
        for connector in self:
            connector.conversation_count = counts.get(connector.id, 0)

    @api.model
    def _selection_linked_accounts(self):
        selection = []
        if 'rn.whatsapp.account' in self.env:
            selection.append(('rn.whatsapp.account', 'WhatsApp Account'))
        return selection

    @api.constrains('bot_id', 'company_id')
    def _check_bot_company(self):
        for connector in self:
            if connector.bot_id and connector.bot_id.company_id not in (
                connector.company_id,
                self.env['res.company'],
            ):
                raise ValidationError('Bot company must match connector company.')

    def action_open_conversations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Conversations',
            'res_model': 'rn.messaging.conversation',
            'view_mode': 'list,form',
            'domain': [('connector_id', '=', self.id)],
            'context': {'default_connector_id': self.id},
        }

    def action_test_simulation(self):
        self.ensure_one()
        self.write({'status': 'connected'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connector ready',
                'message': 'Simulation mode is active. Webhooks will create inbox threads.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_sync_linked_account(self):
        self.ensure_one()
        account = self.linked_account_ref
        if not account or account._name != 'rn.whatsapp.account':
            raise UserError('Select a WhatsApp account from rn_whatsapp_connector first.')
        self.write({
            'channel_type': 'whatsapp',
            'access_token': account.access_token,
            'phone_number_id': account.phone_number_id,
            'business_account_id': account.business_id,
            'phone_number': account.phone_number,
            'api_url': account.api_url or self.api_url,
            'api_version': account.api_version or self.api_version,
            'webhook_verify_token': account.webhook_verify_token,
            'webhook_secret': account.webhook_token,
            'simulation_mode': account.simulation_mode,
            'status': account.status if account.status != 'disconnected' else 'connected',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Account linked',
                'message': 'Connector credentials were copied from the WhatsApp account.',
                'type': 'success',
                'sticky': False,
            },
        }

# -*- coding: utf-8 -*-
"""Conversation channels and account settings."""

from odoo import fields, models


class RnConversationalErpChannel(models.Model):
    _name = 'rn.conversational.erp.channel'
    _description = 'Conversational ERP Channel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    channel_type = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('teams', 'Microsoft Teams'),
            ('slack', 'Slack'),
            ('telegram', 'Telegram'),
            ('voice', 'Voice'),
            ('sms', 'SMS'),
            ('email', 'Email'),
            ('mobile_app', 'Mobile App'),
        ],
        required=True,
        default='whatsapp',
        tracking=True,
    )
    account_ref = fields.Char(string='Account Reference')
    status = fields.Selection(
        [('draft', 'Draft'), ('connected', 'Connected'), ('error', 'Error')],
        default='draft',
        tracking=True,
    )
    simulation_mode = fields.Boolean(default=True)
    assistant_id = fields.Many2one('rn.conversational.erp.assistant', string='Default Assistant')
    conversation_count = fields.Integer(compute='_compute_conversation_count')

    def _compute_conversation_count(self):
        grouped = self.env['rn.conversational.erp.conversation']._read_group(
            [('channel_id', 'in', self.ids)], ['channel_id'], ['__count']
        )
        counts = {channel.id: count for channel, count in grouped}
        for record in self:
            record.conversation_count = counts.get(record.id, 0)

    def action_mark_connected(self):
        self.write({'status': 'connected'})
        return True

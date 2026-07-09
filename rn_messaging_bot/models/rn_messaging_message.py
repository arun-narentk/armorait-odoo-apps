# -*- coding: utf-8 -*-
"""Inbound and outbound channel messages."""

from odoo import fields, models


class RnMessagingMessage(models.Model):
    _name = 'rn.messaging.message'
    _description = 'Messaging Message'
    _order = 'id desc'

    conversation_id = fields.Many2one(
        'rn.messaging.conversation',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(related='conversation_id.company_id', store=True)
    direction = fields.Selection(
        selection=[
            ('inbound', 'Inbound'),
            ('outbound', 'Outbound'),
        ],
        required=True,
        index=True,
    )
    message_type = fields.Selection(
        selection=[
            ('text', 'Text'),
            ('button', 'Button Reply'),
            ('system', 'System'),
        ],
        default='text',
        required=True,
    )
    content = fields.Text(required=True)
    external_message_id = fields.Char(index=True)
    delivery_state = fields.Selection(
        selection=[
            ('received', 'Received'),
            ('queued', 'Queued'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='received',
        index=True,
    )
    priority = fields.Integer(default=10)
    retry_count = fields.Integer(default=0)
    max_retries = fields.Integer(default=3)
    schedule_at = fields.Datetime(string='Send After')
    last_attempt_at = fields.Datetime()
    bot_node_id = fields.Many2one('rn.messaging.bot.node', ondelete='set null')
    template_id = fields.Many2one('rn.messaging.template', ondelete='set null')
    error_message = fields.Char()

# -*- coding: utf-8 -*-
"""Outbound message queue with retry support."""

from __future__ import annotations

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RnMessagingQueueService(models.AbstractModel):
    _name = 'rn.messaging.queue.service'
    _description = 'Messaging Queue Service'

    @api.model
    def enqueue_text(self, conversation, text: str, priority: int = 10):
        message = self.env['rn.messaging.message'].create({
            'conversation_id': conversation.id,
            'direction': 'outbound',
            'message_type': 'text',
            'content': text,
            'delivery_state': 'queued',
            'priority': priority,
        })
        conversation.last_message_at = fields.Datetime.now()
        return message

    @api.model
    def deliver_message(self, message):
        message.ensure_one()
        if message.direction != 'outbound':
            return False
        if message.delivery_state not in ('queued', 'failed'):
            return message.delivery_state == 'sent'
        connector_service = self.env['rn.messaging.connector.service']
        conversation = message.conversation_id
        driver = connector_service.get_driver(conversation.connector_id)
        result = driver.send_text(
            conversation.connector_id,
            conversation,
            message.content,
        )
        vals = {
            'last_attempt_at': fields.Datetime.now(),
            'retry_count': message.retry_count + 1,
            'error_message': result.get('error'),
        }
        if result.get('status') == 'sent':
            vals['delivery_state'] = 'sent'
        else:
            vals['delivery_state'] = 'failed'
        message.write(vals)
        return result.get('status') == 'sent'

    @api.model
    def process_queue(self, limit: int = 50):
        now = fields.Datetime.now()
        messages = self.env['rn.messaging.message'].search([
            ('direction', '=', 'outbound'),
            ('delivery_state', '=', 'queued'),
            '|',
            ('schedule_at', '=', False),
            ('schedule_at', '<=', now),
        ], order='priority desc, id', limit=limit)
        sent = 0
        for message in messages:
            if self.deliver_message(message):
                sent += 1
        _logger.info('Messaging queue processed %s messages (%s sent)', len(messages), sent)
        return len(messages)

    @api.model
    def retry_failed(self, limit: int = 50):
        messages = self.env['rn.messaging.message'].search([
            ('direction', '=', 'outbound'),
            ('delivery_state', '=', 'failed'),
        ], order='priority desc, id', limit=limit)
        to_retry = messages.filtered(
            lambda msg: msg.retry_count < (msg.max_retries or 3)
        )
        if not to_retry:
            return 0
        to_retry.write({'delivery_state': 'queued'})
        return self.process_queue(limit=limit)

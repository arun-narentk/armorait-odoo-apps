# -*- coding: utf-8 -*-
"""Message queue processing."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnWhatsappQueueService(models.AbstractModel):
    _name = 'rn.whatsapp.queue.service'
    _description = 'WhatsApp Queue Service'

    def enqueue(self, message, schedule_at=None, priority=None):
        vals = {'status': 'queued'}
        if schedule_at:
            vals['schedule_at'] = schedule_at
        if priority is not None:
            vals['priority'] = priority
        message.write(vals)
        return message

    def process_queue(self, limit=50):
        now = fields.Datetime.now()
        domain = [
            ('status', '=', 'queued'),
            ('direction', '=', 'outbound'),
            '|',
            ('schedule_at', '=', False),
            ('schedule_at', '<=', now),
        ]
        messages = self.env['rn.whatsapp.message'].search(
            domain,
            order='priority desc, schedule_at, id',
            limit=limit,
        )
        if messages:
            self.env['rn.whatsapp.message.service'].send_messages(messages)
        _logger.info('Processed %s queued WhatsApp messages', len(messages))
        return len(messages)

    def retry_failed(self, limit=50):
        messages = self.env['rn.whatsapp.message'].search([
            ('status', '=', 'failed'),
            ('direction', '=', 'outbound'),
        ], limit=limit)
        to_retry = messages.filtered(lambda m: m.retry_count < (m.max_retries or 3))
        if to_retry:
            to_retry.write({'status': 'queued'})
            return self.process_queue(limit=limit)
        return 0

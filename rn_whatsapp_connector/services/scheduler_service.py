# -*- coding: utf-8 -*-
"""Cron and scheduler helpers."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnWhatsappSchedulerService(models.AbstractModel):
    """Retry failed messages, dispatch scheduled messages, and cleanup logs."""

    _name = 'rn.whatsapp.scheduler.service'
    _description = 'WhatsApp Scheduler Service'

    def cron_retry_failed_messages(self):
        count = self.env['rn.whatsapp.queue.service'].retry_failed(limit=100)
        _logger.info('Retried / re-queued %s failed WhatsApp messages', count)
        return True

    def cron_send_scheduled_messages(self):
        count = self.env['rn.whatsapp.queue.service'].process_queue(limit=100)
        _logger.info('Processed %s scheduled/queued WhatsApp messages', count)
        return True

    def cron_cleanup_webhooks(self):
        cutoff = fields.Datetime.now() - timedelta(days=30)
        old = self.env['rn.whatsapp.webhook'].search([('create_date', '<', cutoff)], limit=500)
        count = len(old)
        old.unlink()
        _logger.info('Removed %s old WhatsApp webhook logs', count)
        return True

    def cron_sync_provider_status(self):
        accounts = self.env['rn.whatsapp.account'].search([('active', '=', True)])
        for account in accounts:
            result = self.env['rn.whatsapp.provider.service'].test_connection(account)
            account.write({
                'status': 'connected' if result.get('ok') else account.status,
                'last_sync': fields.Datetime.now(),
                'connection_state': 'online' if result.get('ok') else account.connection_state,
            })
        return True

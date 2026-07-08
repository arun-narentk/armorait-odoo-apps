# -*- coding: utf-8 -*-
"""Incoming webhook processing."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappWebhookService(models.AbstractModel):
    """Validate, persist, and process provider webhook payloads."""

    _name = 'rn.whatsapp.webhook.service'
    _description = 'WhatsApp Webhook Service'

    def process_payload(self, provider, headers, payload, account=None):
        """Store webhook log and route to provider-specific parser."""
        log = self.env['rn.whatsapp.webhook'].create({
            'name': 'Incoming %s webhook' % provider,
            'provider': provider,
            'account_id': account.id if account else False,
            'headers': str(headers),
            'payload': str(payload),
            'status': 'received',
        })
        _logger.info('Webhook log %s stored (Phase 8).', log.id)
        return log

    def validate_signature(self, provider, headers, payload, secret):
        """Verify webhook authenticity before processing."""
        # Phase 8: provider-specific HMAC validation.
        return False

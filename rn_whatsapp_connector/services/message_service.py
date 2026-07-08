# -*- coding: utf-8 -*-
"""Outbound message orchestration."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappMessageService(models.AbstractModel):
    """Build, validate, queue, and dispatch WhatsApp messages."""

    _name = 'rn.whatsapp.message.service'
    _description = 'WhatsApp Message Service'

    def build_text_message(self, account, phone, body, partner=None):
        """Create a draft text message record ready for queueing."""
        vals = {
            'account_id': account.id,
            'phone': phone,
            'body': body,
            'message_type': 'text',
            'direction': 'outbound',
            'partner_id': partner.id if partner else False,
        }
        return self.env['rn.whatsapp.message'].create(vals)

    def send_message(self, message):
        """Dispatch a queued message through the provider layer."""
        message.ensure_one()
        _logger.info('Send requested for WhatsApp message %s (Phase 4).', message.uuid)
        return False

    def parse_template_variables(self, template, values):
        """Replace {{variable}} placeholders in a template body."""
        body = template.body or ''
        for key, value in (values or {}).items():
            body = body.replace('{{%s}}' % key, str(value))
        return body

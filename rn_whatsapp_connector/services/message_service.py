# -*- coding: utf-8 -*-
"""Outbound message orchestration."""

import json
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnWhatsappMessageService(models.AbstractModel):
    """Build, validate, queue, and dispatch WhatsApp messages."""

    _name = 'rn.whatsapp.message.service'
    _description = 'WhatsApp Message Service'

    def build_text_message(self, account, phone, body, partner=None, **extra):
        vals = {
            'account_id': account.id,
            'phone': phone,
            'body': body,
            'message_type': 'text',
            'direction': 'outbound',
            'partner_id': partner.id if partner else False,
            'company_id': account.company_id.id,
        }
        vals.update(extra)
        return self.env['rn.whatsapp.message'].create(vals)

    def build_template_message(self, account, phone, template, variables=None, partner=None, **extra):
        vals = {
            'account_id': account.id,
            'phone': phone,
            'template_id': template.id,
            'message_type': 'template',
            'direction': 'outbound',
            'body': self.env['rn.whatsapp.template.service'].render(template, variables or {}),
            'template_vars': json.dumps(variables or {}),
            'partner_id': partner.id if partner else False,
            'company_id': account.company_id.id,
        }
        vals.update(extra)
        return self.env['rn.whatsapp.message'].create(vals)

    def send_message(self, message):
        return self.send_messages(message)

    def send_messages(self, messages):
        History = self.env['rn.whatsapp.history']
        for message in messages:
            if message.status == 'cancelled':
                continue
            if message.direction != 'outbound':
                continue
            result = self.env['rn.whatsapp.provider.service'].send_message(message)
            if result.get('ok'):
                message.write({
                    'status': 'sent',
                    'provider_message_id': result.get('provider_message_id'),
                    'provider_response': json.dumps(result.get('raw') or {}),
                    'sent_at': fields.Datetime.now(),
                    'error_message': False,
                })
                message.account_id.messages_today += 1
                History.create({
                    'message_id': message.id,
                    'event_type': 'sent',
                    'description': 'Provider accepted message',
                    })
            else:
                message.write({
                    'status': 'failed',
                    'error_message': result.get('error') or 'Send failed',
                    'provider_response': json.dumps(result.get('raw') or {}),
                    'failed_at': fields.Datetime.now(),
                    'retry_count': message.retry_count + 1,
                })
                History.create({
                    'message_id': message.id,
                    'event_type': 'failed',
                    'description': message.error_message,
                    })
            _logger.info('WhatsApp message %s -> %s', message.uuid, message.status)
        return True

    def parse_template_variables(self, template, values):
        return self.env['rn.whatsapp.template.service'].render(template, values)

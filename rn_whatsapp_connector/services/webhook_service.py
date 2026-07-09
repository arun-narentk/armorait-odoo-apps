# -*- coding: utf-8 -*-
"""Webhook intake and status mapping."""

import json
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnWhatsappWebhookService(models.AbstractModel):
    _name = 'rn.whatsapp.webhook.service'
    _description = 'WhatsApp Webhook Service'

    def process_payload(self, provider, headers, payload):
        account = self.env['rn.whatsapp.account'].sudo().search([
            ('provider', '=', provider if provider != 'meta' else 'meta_cloud'),
            ('active', '=', True),
        ], limit=1)
        log = self.env['rn.whatsapp.webhook'].sudo().create({
            'name': 'Webhook %s' % (provider or 'unknown'),
            'provider': account.provider if account else (provider or 'meta_cloud'),
            'payload': payload if isinstance(payload, str) else json.dumps(payload),
            'headers': json.dumps({k: str(v) for k, v in (headers or {}).items()}),
            'account_id': account.id if account else False,
            'company_id': account.company_id.id if account else self.env.company.id,
            'status': 'received',
        })
        try:
            data = json.loads(payload) if isinstance(payload, str) else (payload or {})
        except (TypeError, ValueError):
            data = {}
        self._apply_status_updates(account, data)
        self._apply_inbound(account, data)
        log.status = 'processed'
        _logger.info('Processed WhatsApp webhook %s', log.id)
        return True

    def _apply_status_updates(self, account, data):
        # Meta-style statuses
        entries = []
        for entry in data.get('entry', []) if isinstance(data, dict) else []:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for status in value.get('statuses', []):
                    entries.append(status)
        Message = self.env['rn.whatsapp.message'].sudo()
        for status in entries:
            msg_id = status.get('id')
            state = status.get('status')
            message = Message.search([('provider_message_id', '=', msg_id)], limit=1)
            if not message:
                continue
            vals = {}
            if state == 'delivered':
                vals = {'status': 'delivered', 'delivered_at': fields.Datetime.now()}
            elif state == 'read':
                vals = {'status': 'read', 'read_at': fields.Datetime.now()}
            elif state == 'failed':
                vals = {'status': 'failed', 'failed_at': fields.Datetime.now(), 'error_message': str(status.get('errors'))}
            if vals:
                message.write(vals)

    def _apply_inbound(self, account, data):
        if not account:
            return
        for entry in data.get('entry', []) if isinstance(data, dict) else []:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for msg in value.get('messages', []):
                    phone = msg.get('from')
                    body = (msg.get('text') or {}).get('body') or msg.get('type')
                    self.env['rn.whatsapp.message'].sudo().create({
                        'account_id': account.id,
                        'phone': phone,
                        'body': body,
                        'message_type': 'text',
                        'direction': 'inbound',
                        'status': 'delivered',
                        'provider_message_id': msg.get('id'),
                        'company_id': account.company_id.id,
                    })

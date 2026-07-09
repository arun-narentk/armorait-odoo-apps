# -*- coding: utf-8 -*-
"""Webhook intake and conversation bootstrap."""

from __future__ import annotations

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RnMessagingWebhookService(models.AbstractModel):
    _name = 'rn.messaging.webhook.service'
    _description = 'Messaging Webhook Service'

    @api.model
    def verify_token(self, connector, token: str) -> bool:
        expected = connector.webhook_verify_token or ''
        return bool(expected) and token == expected

    @api.model
    def ingest_payload(self, connector, payload: dict):
        driver = self.env['rn.messaging.connector.service'].get_driver(connector)
        normalized_messages = driver.normalize_inbound(payload)
        conversations = self.env['rn.messaging.conversation']
        for item in normalized_messages:
            conversation = self._get_or_create_conversation(connector, item)
            self.env['rn.messaging.message'].create({
                'conversation_id': conversation.id,
                'direction': 'inbound',
                'message_type': item.get('message_type', 'text'),
                'content': item.get('content') or '',
                'external_message_id': item.get('external_message_id'),
                'delivery_state': 'received',
            })
            conversation.last_message_at = fields.Datetime.now()
            self.env['rn.messaging.bot.engine.service'].process_inbound(
                conversation,
                item.get('content') or '',
            )
            conversations |= conversation
        return conversations

    @api.model
    def _get_or_create_conversation(self, connector, item: dict):
        external_id = item.get('external_contact_id')
        Conversation = self.env['rn.messaging.conversation']
        conversation = Conversation.search([
            ('connector_id', '=', connector.id),
            ('external_contact_id', '=', external_id),
            ('state', '!=', 'closed'),
        ], limit=1)
        if conversation:
            return conversation
        partner = self._find_or_create_partner(item)
        name = item.get('contact_name') or external_id or 'Messaging Contact'
        return Conversation.create({
            'name': name,
            'connector_id': connector.id,
            'partner_id': partner.id,
            'external_contact_id': external_id,
            'state': 'bot',
        })

    @api.model
    def _find_or_create_partner(self, item: dict):
        Partner = self.env['res.partner']
        external_id = item.get('external_contact_id')
        partner = Partner.search([
            ('rn_messaging_external_ids', 'ilike', external_id),
        ], limit=1)
        if partner:
            return partner
        name = item.get('contact_name') or external_id or 'Messaging Contact'
        return Partner.create({
            'name': name,
            'phone': external_id if external_id and external_id.isdigit() else False,
            'rn_messaging_external_ids': external_id,
            'company_id': False,
        })

# -*- coding: utf-8 -*-
"""Bot flow execution for inbound customer messages."""

from __future__ import annotations

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class RnMessagingBotEngineService(models.AbstractModel):
    _name = 'rn.messaging.bot.engine.service'
    _description = 'Messaging Bot Engine Service'

    @api.model
    def process_inbound(self, conversation, inbound_text: str):
        connector = conversation.connector_id
        if conversation.state == 'human' or not connector.bot_id:
            return False
        bot = connector.bot_id
        session = conversation.bot_session_id
        if not session or session.state != 'running':
            session = self._create_session(conversation, bot)
        node = session.current_node_id or bot.start_node_id
        if not node:
            self.env['rn.messaging.connector.service'].send_text(
                conversation,
                bot.welcome_text or _('Thanks for your message.'),
            )
            return True
        return self._run_node(conversation, session, node, inbound_text)

    @api.model
    def _create_session(self, conversation, bot):
        session = self.env['rn.messaging.bot.session'].create({
            'name': f'{bot.name} / {conversation.name}',
            'bot_id': bot.id,
            'conversation_id': conversation.id,
            'current_node_id': bot.start_node_id.id if bot.start_node_id else False,
            'state': 'running',
        })
        conversation.write({
            'bot_session_id': session.id,
            'state': 'bot',
        })
        if bot.welcome_text:
            self.env['rn.messaging.connector.service'].send_text(conversation, bot.welcome_text)
        return session

    @api.model
    def _run_node(self, conversation, session, node, inbound_text: str):
        connector_service = self.env['rn.messaging.connector.service']
        if node.node_type == 'message':
            if node.body_text:
                connector_service.send_text(conversation, node.body_text)
            next_node = node.next_node_id
            session.current_node_id = next_node.id if next_node else False
            if next_node:
                return self._run_node(conversation, session, next_node, inbound_text)
            session.state = 'completed'
            return True
        if node.node_type == 'menu':
            matched = self._match_option(node, inbound_text)
            if matched:
                return self._run_node(conversation, session, matched, inbound_text)
            options_text = '\n'.join(
                f"- {option.name}" for option in node.option_ids.sorted('sequence')
            )
            prompt = node.body_text or _('Please choose an option:')
            connector_service.send_text(conversation, f'{prompt}\n{options_text}'.strip())
            return True
        if node.node_type == 'action':
            self._run_action(conversation, node)
            next_node = node.next_node_id
            session.current_node_id = next_node.id if next_node else False
            if not next_node:
                session.state = 'completed'
            return True
        if node.node_type == 'handoff':
            conversation.action_handoff_human()
            connector_service.send_text(
                conversation,
                _('A team member will join this chat shortly.'),
            )
            session.state = 'handoff'
            return True
        return False

    @api.model
    def _match_option(self, node, inbound_text: str):
        text = (inbound_text or '').strip().lower()
        for option in node.option_ids.sorted('sequence'):
            keyword = (option.keyword or '').strip().lower()
            if keyword == '*' or keyword == text or keyword in text:
                return option.target_node_id
        return node.fallback_node_id

    @api.model
    def _run_action(self, conversation, node):
        if node.action_code == 'create_lead' and not conversation.lead_id:
            conversation._create_lead_record()
            self.env['rn.messaging.connector.service'].send_text(
                conversation,
                _('Thanks. We created a follow-up request for our team.'),
            )

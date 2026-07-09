# -*- coding: utf-8 -*-
"""Conversation routing and approval helpers."""

from odoo import models


class RnConversationalErpRouterService(models.AbstractModel):
    _name = 'rn.conversational.erp.router.service'
    _description = 'Conversational ERP Router Service'

    def route_message(self, channel, external_contact_id, text, partner=None, user=None):
        conversation = self.env['rn.conversational.erp.conversation'].create({
            'channel_id': channel.id,
            'assistant_id': channel.assistant_id.id,
            'partner_id': partner.id if partner else False,
            'user_id': user.id if user else False,
            'external_contact_id': external_contact_id,
            'intent': self._detect_intent(text),
        })
        conversation.post_message('inbound', text, actor_name=partner.name if partner else 'Contact')
        response = self._build_response(conversation, text)
        conversation.post_message('outbound', response['message'])
        if response.get('create_approval'):
            self.env['rn.conversational.erp.approval'].create({
                'conversation_id': conversation.id,
                'approver_id': self.env.user.id,
                'summary': response['create_approval'],
                'amount': response.get('amount', 0.0),
            })
        return conversation

    def _detect_intent(self, text):
        text_lower = (text or '').lower()
        if any(word in text_lower for word in ['approve', 'approval', 'po', 'purchase']):
            return 'approval'
        if any(word in text_lower for word in ['leave', 'holiday', 'attendance']):
            return 'hr'
        if any(word in text_lower for word in ['stock', 'inventory', 'warehouse']):
            return 'inventory'
        if any(word in text_lower for word in ['sales', 'quotation', 'quote']):
            return 'sales'
        if any(word in text_lower for word in ['today', 'cash', 'collection', 'ceo', 'revenue']):
            return 'executive'
        return 'general'

    def _build_response(self, conversation, text):
        intent = conversation.intent
        if intent == 'approval':
            return {
                'message': 'Approval request captured. Review the approval center for the next action.',
                'create_approval': 'Conversational approval captured from incoming request.',
                'amount': 0.0,
            }
        if intent == 'hr':
            return {'message': 'HR request understood. Please confirm the reason so the leave request can be prepared.'}
        if intent == 'inventory':
            return {'message': 'Inventory query received. I can summarize on-hand, incoming, and reserved stock.'}
        if intent == 'sales':
            return {'message': 'Sales request captured. I can guide quotation creation and pricing confirmation.'}
        if intent == 'executive':
            return {'message': 'Executive summary ready. I can provide sales, collections, approvals, and operational alerts.'}
        return {'message': 'Message received. I can help with approvals, HR, inventory, sales, and executive summaries.'}

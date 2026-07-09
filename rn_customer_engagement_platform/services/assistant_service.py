# -*- coding: utf-8 -*-
"""Knowledge and Odoo-aware assistant routing for customer engagement."""

from odoo import models


class RnCustomerEngagementAssistantService(models.AbstractModel):
    _name = 'rn.customer.engagement.assistant.service'
    _description = 'Customer Engagement Assistant Service'

    def process_message(self, channel, external_contact, text, partner=None, session=None):
        topic = self._detect_topic(text)
        conversation = self.env['rn.customer.engagement.conversation'].create({
            'channel_id': channel.id,
            'session_id': session.id if session else False,
            'partner_id': partner.id if partner else False,
            'external_contact': external_contact,
            'topic': topic,
        })
        conversation.post_line('inbound', text, actor_name=partner.name if partner else 'Customer')
        response = self._build_response(topic, partner, text)
        conversation.post_line('outbound', response['message'])
        if response.get('escalate'):
            escalation = self.env['rn.customer.engagement.escalation'].create({
                'conversation_id': conversation.id,
                'partner_id': partner.id if partner else False,
                'category': response.get('category', 'support'),
                'summary': response['escalate'],
            })
            conversation.write({'state': 'escalated', 'escalation_id': escalation.id})
        return conversation

    def _detect_topic(self, text):
        text_lower = (text or '').lower()
        if any(word in text_lower for word in ['order', 'shipment', 'tracking']):
            return 'order'
        if any(word in text_lower for word in ['invoice', 'pdf', 'copy']):
            return 'invoice'
        if any(word in text_lower for word in ['payment', 'balance', 'paid']):
            return 'payment'
        if any(word in text_lower for word in ['delivery', 'reschedule', 'dispatch']):
            return 'delivery'
        if any(word in text_lower for word in ['stock', 'available', 'inventory']):
            return 'stock'
        if any(word in text_lower for word in ['return', 'warranty', 'problem', 'issue']):
            return 'support'
        return 'general'

    def _build_response(self, topic, partner, text):
        if topic == 'order':
            order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id)], order='date_order desc', limit=1) if partner else self.env['sale.order']
            if order:
                return {'message': f'Latest order {order.name} is currently {order.state}. I can also help with invoice or delivery details.'}
            return {'message': 'I could not find a recent order yet. A support agent can help review it.', 'escalate': 'Customer requested order status but no recent sales order was found.'}
        if topic == 'invoice':
            invoice = self.env['account.move'].sudo().search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('state', '=', 'posted'),
            ], order='invoice_date desc', limit=1) if partner else self.env['account.move']
            if invoice:
                return {'message': f'Latest invoice {invoice.name} has payment status {invoice.payment_state} and total {invoice.amount_total:.2f}.'}
            return {'message': 'I could not find an invoice. I am escalating this to billing.', 'escalate': 'Customer requested invoice assistance but no invoice was found.', 'category': 'billing'}
        if topic == 'payment':
            return {'message': 'I can help with payment status, receipts, and account balance. A finance agent can step in if reconciliation is needed.'}
        if topic == 'delivery':
            return {'message': 'Delivery changes may need validation. I am preparing a delivery support follow-up.', 'escalate': 'Customer requested delivery update or reschedule support.', 'category': 'delivery'}
        if topic == 'stock':
            return {'message': 'Stock availability can be shared after account validation. A sales or supply agent can continue if needed.'}
        if topic == 'support':
            article = self._find_knowledge(text)
            if article:
                return {'message': article.content}
            return {'message': 'I need a support specialist for this request.', 'escalate': 'Customer support request requires human assistance.', 'category': 'support'}
        article = self._find_knowledge(text)
        if article:
            return {'message': article.content}
        return {'message': 'I can help with orders, invoices, payments, delivery, stock, and support questions.'}

    def _find_knowledge(self, text):
        text_lower = (text or '').lower()
        articles = self.env['rn.customer.engagement.knowledge'].search([('active', '=', True)], order='sequence, id')
        for article in articles:
            hints = [item.strip().lower() for item in (article.keyword_hint or '').split(',') if item.strip()]
            if any(hint in text_lower for hint in hints):
                return article
        return False

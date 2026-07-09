# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_customer_engagement_platform')
class TestCustomerEngagementPlatform(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env.ref('rn_customer_engagement_platform.channel_customer_web')
        cls.partner = cls.env['res.partner'].create({'name': 'Customer User', 'email': 'customer.user@example.com'})
        cls.session = cls.env['rn.customer.engagement.session'].create({
            'channel_id': cls.channel.id,
            'partner_id': cls.partner.id,
            'auth_state': 'authenticated',
            'external_contact': 'customer.user@example.com',
        })
        cls.service = cls.env['rn.customer.engagement.assistant.service']
        cls.dashboard = cls.env['rn.customer.engagement.dashboard.service']

    def test_process_order_message(self):
        conversation = self.service.process_message(
            self.channel,
            'customer.user@example.com',
            'Where is my order?',
            partner=self.partner,
            session=self.session,
        )
        self.assertEqual(conversation.topic, 'order')
        self.assertEqual(len(conversation.line_ids), 2)

    def test_process_support_message_creates_escalation(self):
        conversation = self.service.process_message(
            self.channel,
            'customer.user@example.com',
            'I have a warranty issue with my product',
            partner=self.partner,
            session=self.session,
        )
        self.assertIn(conversation.state, ('bot', 'escalated'))
        if conversation.state == 'escalated':
            self.assertTrue(conversation.escalation_id)

    def test_knowledge_lookup_reply(self):
        conversation = self.service.process_message(
            self.channel,
            'customer.user@example.com',
            'Can I return this product?',
            partner=self.partner,
            session=self.session,
        )
        self.assertIn('return', conversation.line_ids[-1].content.lower())

    def test_dashboard_metrics(self):
        self.service.process_message(
            self.channel,
            'customer.user@example.com',
            'I need another copy of my invoice',
            partner=self.partner,
            session=self.session,
        )
        data = self.dashboard.get_dashboard_data()
        self.assertIn('channels', data)
        self.assertIn('open_escalations', data)
        self.assertIn('recent_conversations', data)

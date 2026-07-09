# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'rn_messaging_bot')
class TestMessagingBot(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Webhook = cls.env['rn.messaging.webhook.service']
        cls.BotEngine = cls.env['rn.messaging.bot.engine.service']
        cls.Queue = cls.env['rn.messaging.queue.service']
        cls.bot = cls.env.ref('rn_messaging_bot.bot_support_flow')
        cls.connector = cls.env['rn.messaging.connector'].create({
            'name': 'Test WhatsApp Connector',
            'channel_type': 'whatsapp',
            'simulation_mode': True,
            'status': 'connected',
            'bot_id': cls.bot.id,
            'webhook_verify_token': 'armora-test-token',
        })

    def test_webhook_verify_token(self):
        self.assertTrue(self.Webhook.verify_token(self.connector, 'armora-test-token'))
        self.assertFalse(self.Webhook.verify_token(self.connector, 'wrong-token'))

    def test_ingest_creates_conversation_and_welcome(self):
        conversations = self.Webhook.ingest_payload(self.connector, {
            'from': '919999999999',
            'name': 'Test User',
            'text': 'hello',
        })
        self.assertEqual(len(conversations), 1)
        conversation = conversations[0]
        self.assertEqual(conversation.external_contact_id, '919999999999')
        self.assertEqual(conversation.state, 'bot')
        self.assertTrue(conversation.bot_session_id)
        inbound = conversation.message_ids.filtered(lambda msg: msg.direction == 'inbound')
        outbound = conversation.message_ids.filtered(lambda msg: msg.direction == 'outbound')
        self.assertEqual(len(inbound), 1)
        self.assertGreaterEqual(len(outbound), 1)
        self.assertIn(self.bot.welcome_text, outbound.mapped('content'))

    def test_sales_menu_creates_crm_lead(self):
        conversations = self.Webhook.ingest_payload(self.connector, {
            'from': '918888888888',
            'name': 'Lead User',
            'text': 'sales',
        })
        conversation = conversations[0]
        self.assertTrue(conversation.lead_id)
        self.assertEqual(conversation.lead_id.partner_id, conversation.partner_id)
        outbound = conversation.message_ids.filtered(lambda msg: msg.direction == 'outbound')
        self.assertTrue(any('sales team' in (msg.content or '').lower() for msg in outbound))

    def test_human_handoff_stops_bot(self):
        conversations = self.Webhook.ingest_payload(self.connector, {
            'from': '917777777777',
            'name': 'Handoff User',
            'text': 'human',
        })
        conversation = conversations[0]
        self.assertEqual(conversation.state, 'human')
        self.assertEqual(conversation.bot_session_id.state, 'handoff')
        before_count = len(conversation.message_ids)
        self.BotEngine.process_inbound(conversation, 'another message')
        self.assertEqual(len(conversation.message_ids), before_count)

    def test_agent_reply_wizard_sends_outbound(self):
        conversation = self.Webhook.ingest_payload(self.connector, {
            'from': '916666666666',
            'name': 'Agent Test',
            'text': 'hello',
        })[0]
        wizard = self.env['rn.messaging.compose.reply.wizard'].create({
            'conversation_id': conversation.id,
            'body': 'Thanks for reaching out. An agent will help you now.',
        })
        wizard.action_send()
        self.assertEqual(conversation.state, 'human')
        outbound = conversation.message_ids.filtered(
            lambda msg: msg.direction == 'outbound' and 'agent will help' in (msg.content or '').lower()
        )
        self.assertTrue(outbound)
        self.assertEqual(outbound.delivery_state, 'sent')

    def test_facebook_webhook_normalization(self):
        connector = self.connector.copy({
            'name': 'Facebook Connector',
            'channel_type': 'facebook',
            'page_id': '123456789',
        })
        payload = {
            'object': 'page',
            'entry': [{
                'messaging': [{
                    'sender': {'id': 'psid-001'},
                    'message': {'mid': 'm1', 'text': 'Need pricing'},
                }],
            }],
        }
        conversations = self.Webhook.ingest_payload(connector, payload)
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations.external_contact_id, 'psid-001')

    def test_queue_retry_failed_message(self):
        conversation = self.env['rn.messaging.conversation'].create({
            'name': 'Queue Test',
            'connector_id': self.connector.id,
            'external_contact_id': 'queue-user',
            'state': 'human',
        })
        message = self.Queue.enqueue_text(conversation, 'Retry me please')
        message.write({
            'delivery_state': 'failed',
            'retry_count': 0,
        })
        self.Queue.retry_failed()
        message.invalidate_recordset()
        self.assertEqual(message.delivery_state, 'sent')

    def test_flow_designer_data_and_layout_save(self):
        data = self.bot.get_designer_data(self.bot.id)
        self.assertTrue(data['nodes'])
        self.assertTrue(data['edges'])
        node = self.bot.node_ids[:1]
        self.bot.save_designer_layout(self.bot.id, [{
            'id': node.id,
            'pos_x': 150.0,
            'pos_y': 250.0,
        }])
        node.invalidate_recordset()
        self.assertEqual(node.pos_x, 150.0)
        self.assertEqual(node.pos_y, 250.0)

# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_conversational_erp')
class TestConversationalErp(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.assistant = cls.env.ref('rn_conversational_erp.assistant_employee_ai')
        cls.channel = cls.env['rn.conversational.erp.channel'].create({
            'name': 'Test WhatsApp Channel',
            'channel_type': 'whatsapp',
            'assistant_id': cls.assistant.id,
            'status': 'connected',
            'simulation_mode': True,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Conversation User', 'phone': '919999999999'})
        cls.router = cls.env['rn.conversational.erp.router.service']
        cls.dashboard = cls.env['rn.conversational.erp.dashboard.service']

    def test_route_hr_message(self):
        conversation = self.router.route_message(
            self.channel,
            '919999999999',
            'Apply leave tomorrow',
            partner=self.partner,
        )
        self.assertEqual(conversation.intent, 'hr')
        self.assertEqual(len(conversation.line_ids), 2)
        self.assertIn('leave request', conversation.line_ids[-1].content.lower())

    def test_route_approval_creates_approval_center_record(self):
        conversation = self.router.route_message(
            self.channel,
            '918888888888',
            'Approve purchase order PO-245',
            partner=self.partner,
        )
        self.assertEqual(conversation.intent, 'approval')
        self.assertTrue(conversation.approval_ids)
        self.assertEqual(conversation.approval_ids[0].state, 'pending')

    def test_approval_actions(self):
        approval = self.env['rn.conversational.erp.approval'].create({
            'approver_id': self.env.user.id,
            'summary': 'Approve expense claim',
        })
        approval.action_approve()
        self.assertEqual(approval.state, 'approved')
        approval.write({'state': 'pending'})
        approval.action_reject()
        self.assertEqual(approval.state, 'rejected')

    def test_dashboard_metrics(self):
        self.router.route_message(self.channel, '917777777777', 'Today sales summary', partner=self.partner)
        data = self.dashboard.get_dashboard_data()
        self.assertIn('channels', data)
        self.assertIn('pending_approvals', data)
        self.assertIn('recent_conversations', data)

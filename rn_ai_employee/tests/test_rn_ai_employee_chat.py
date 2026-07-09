# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'rn_ai_employee')
class TestAiEmployeeChat(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Chat = cls.env['rn.ai.employee.chat']
        cls.Service = cls.env['rn.ai.employee.service']
        cls.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'True')

    def test_chat_creation_adds_system_message(self):
        chat = self.Chat.create({'name': 'Test chat'})
        roles = chat.message_ids.mapped('role')
        self.assertIn('system', roles)

    def test_overdue_question_creates_action_cards(self):
        chat = self.Chat.create({'name': 'Overdue test'})
        self.Service.process_chat_message(chat, 'Show overdue invoices')
        assistant = chat.message_ids.filtered(lambda msg: msg.role == 'assistant')
        self.assertTrue(assistant)
        self.assertTrue(assistant[0].headline)
        self.assertTrue(assistant[0].action_ids)

    def test_unknown_question_returns_guidance(self):
        chat = self.Chat.create({'name': 'Guidance test'})
        self.Service.process_chat_message(chat, 'xyzzy unknown question')
        assistant = chat.message_ids.filtered(lambda msg: msg.role == 'assistant')[-1]
        self.assertIn('business questions', assistant.content.lower())

    def test_suggested_question_routes_directly(self):
        suggestion = self.env['rn.ai.employee.suggestion'].search([], limit=1)
        chat = self.Chat.create({'name': 'Suggestion test'})
        self.Service.process_chat_message(chat, suggestion.question)
        tool_messages = chat.message_ids.filtered(lambda msg: msg.role == 'tool')
        self.assertTrue(tool_messages)
        self.assertEqual(tool_messages[0].tool_name, suggestion.tool_name)

    def test_disabled_copilot_blocks_processing(self):
        chat = self.Chat.create({'name': 'Disabled test'})
        self.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'False')
        with self.assertRaises(UserError):
            self.Service.process_chat_message(chat, 'Show overdue invoices')
        self.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'True')

# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'rn_ai_employee')
class TestAiEmployeePhase2(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tool = cls.env['rn.ai.employee.tool']
        cls.Chat = cls.env['rn.ai.employee.chat']
        cls.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'True')

    def test_intent_detect_create_quotation(self):
        tool_name, _args = self.env['rn.ai.employee.intent'].detect('Create a quotation for pumps')
        self.assertEqual(tool_name, 'create_quotation')

    def test_intent_detect_payment_reminders(self):
        tool_name, _args = self.env['rn.ai.employee.intent'].detect('Send reminder emails to overdue customers')
        self.assertEqual(tool_name, 'send_payment_reminders')

    def test_create_quotation_tool_creates_sale_order(self):
        partner = self.env['res.partner'].create({
            'name': 'Demo Pump Customer',
            'customer_rank': 1,
        })
        self.env['product.product'].create({
            'name': 'Industrial Pump',
            'list_price': 150.0,
            'type': 'consu',
        })
        result = self.Tool.execute_by_name('create_quotation', {
            'partner_name': 'Demo Pump',
            'product_name': 'Pump',
            'quantity': 5,
        })
        self.assertNotIn('error', result)
        self.assertEqual(result.get('model'), 'sale.order')
        order = self.env['sale.order'].browse(result['record_ids'])
        self.assertEqual(order.partner_id, partner)
        self.assertEqual(order.order_line.product_id.name, 'Industrial Pump')
        open_form = [action for action in result['suggested_actions'] if action['action_type'] == 'open_form']
        self.assertTrue(open_form)

    def test_send_payment_reminders_without_invoices(self):
        result = self.Tool.execute_by_name('send_payment_reminders', {'days_overdue': 0, 'limit': 5})
        self.assertIn('headline', result)
        self.assertEqual(result.get('model'), 'account.move')

    def test_open_form_action_card(self):
        partner = self.env['res.partner'].create({'name': 'Action Partner', 'customer_rank': 1})
        message = self.env['rn.ai.employee.message'].create({
            'chat_id': self.Chat.create({'name': 'Open form test'}).id,
            'role': 'assistant',
            'content': 'Created',
        })
        action = self.env['rn.ai.employee.message.action'].create({
            'message_id': message.id,
            'label': 'Open Partner',
            'action_type': 'open_form',
            'res_model': 'res.partner',
            'res_ids': str([partner.id]),
        })
        client_action = action.action_run()
        self.assertEqual(client_action['res_model'], 'res.partner')
        self.assertEqual(client_action['res_id'], partner.id)
        self.assertEqual(client_action['view_mode'], 'form')

    def test_widget_bootstrap_and_send(self):
        bootstrap = self.Chat.widget_bootstrap()
        self.assertTrue(bootstrap['chat_id'])
        self.assertTrue(bootstrap['messages'])
        self.assertTrue(bootstrap['suggestions'])
        payload = self.Chat.widget_send_message(bootstrap['chat_id'], 'Show overdue invoices')
        self.assertTrue(any(msg['role'] == 'assistant' for msg in payload['messages']))

    def test_widget_disabled_blocks_access(self):
        self.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'False')
        with self.assertRaises(UserError):
            self.Chat.widget_bootstrap()
        self.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'True')

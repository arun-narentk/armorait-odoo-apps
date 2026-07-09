# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'rn_ai_employee')
class TestAiEmployeeTools(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tool = cls.env['rn.ai.employee.tool']

    def test_registry_contains_phase1_tools(self):
        technical_names = set(self.Tool.search([]).mapped('model_name'))
        expected = {
            'today_sales', 'pending_quotations', 'overdue_invoices',
            'low_stock', 'revenue_this_month', 'top_customers',
        }
        self.assertTrue(expected.issubset(technical_names))

    def test_overdue_invoices_returns_structured_payload(self):
        result = self.Tool.execute_by_name('overdue_invoices', {'days_overdue': 90})
        self.assertIn('headline', result)
        self.assertIn('suggested_actions', result)
        self.assertIn('model', result)

    def test_today_sales_runs(self):
        result = self.Tool.execute_by_name('today_sales', {})
        self.assertIn('headline', result)
        self.assertEqual(result.get('category'), 'sales')

    def test_find_customer_inactive(self):
        result = self.Tool.execute_by_name('find_customer', {'inactive_months': 6})
        self.assertIn('headline', result)

    def test_open_list_action_card_opens_target_model(self):
        result = self.Tool.execute_by_name('overdue_invoices', {'days_overdue': 90})
        message = self.env['rn.ai.employee.message'].create({
            'chat_id': self.env['rn.ai.employee.chat'].create({'name': 'Action test'}).id,
            'role': 'assistant',
            'content': 'Action card test',
            'headline': result['headline'],
        })
        self.env['rn.ai.employee.message.action'].create_from_tool_result(message, result)
        action_card = message.action_ids.filtered(lambda rec: rec.action_type == 'open_list')[:1]
        self.assertTrue(action_card)
        action = action_card.action_run()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], result['model'])

    def test_create_activity_action_requires_records(self):
        action = self.env['rn.ai.employee.message.action'].create({
            'message_id': self.env['rn.ai.employee.message'].create({
                'chat_id': self.env['rn.ai.employee.chat'].create({'name': 'Empty activity test'}).id,
                'role': 'assistant',
                'content': 'Missing records',
            }).id,
            'label': 'Create Activity',
            'action_type': 'create_activity',
            'res_model': 'account.move',
            'res_ids': '[]',
        })
        with self.assertRaises(UserError):
            action.action_run()

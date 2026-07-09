# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'rn_ai_employee')
class TestAiEmployeePhase4(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Agent = cls.env['rn.ai.employee.agent']
        cls.Chat = cls.env['rn.ai.employee.chat']
        cls.Intent = cls.env['rn.ai.employee.intent']
        cls.Service = cls.env['rn.ai.employee.service']
        cls.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'True')

    def test_domain_agents_installed(self):
        sales = self.Agent.search([('code', '=', 'sales')], limit=1)
        finance = self.Agent.search([('code', '=', 'finance')], limit=1)
        executive = self.Agent.search([('code', '=', 'executive')], limit=1)
        self.assertTrue(sales and finance and executive)
        self.assertGreater(len(sales.tool_ids), 5)
        self.assertIn('overdue_invoices', finance.tool_ids.mapped('model_name'))
        self.assertIn('morning_briefing', executive.tool_ids.mapped('model_name'))

    def test_sales_agent_blocks_finance_tool(self):
        sales = self.Agent.search([('code', '=', 'sales')], limit=1)
        chat = self.Chat.create({'name': 'Sales scope', 'agent_id': sales.id})
        allowed = set(sales.tool_ids.mapped('model_name'))
        tool_name, _args = self.Intent.detect('Show overdue invoices', allowed_tools=allowed)
        self.assertFalse(tool_name)

    def test_finance_agent_resolves_overdue_invoices(self):
        finance = self.Agent.search([('code', '=', 'finance')], limit=1)
        allowed = set(finance.tool_ids.mapped('model_name'))
        tool_name, _args = self.Intent.detect('Show overdue invoices', allowed_tools=allowed)
        self.assertEqual(tool_name, 'overdue_invoices')

    def test_executive_agent_resolves_morning_briefing(self):
        executive = self.Agent.search([('code', '=', 'executive')], limit=1)
        allowed = set(executive.tool_ids.mapped('model_name'))
        tool_name, _args = self.Intent.detect('Show my morning briefing', allowed_tools=allowed)
        self.assertEqual(tool_name, 'morning_briefing')

    def test_chat_with_agent_uses_scoped_suggestions(self):
        finance = self.Agent.search([('code', '=', 'finance')], limit=1)
        from ..services.agent_service import get_agent_service

        suggestions = get_agent_service(self.env).get_suggestions(finance, limit=6)
        self.assertTrue(suggestions)
        self.assertTrue(all(s.tool_name in finance.tool_ids.mapped('model_name') for s in suggestions if s.tool_name))

    def test_widget_bootstrap_returns_agents(self):
        bootstrap = self.Chat.widget_bootstrap()
        self.assertIn('agents', bootstrap)
        self.assertGreaterEqual(len(bootstrap['agents']), 3)
        self.assertIn('agent_id', bootstrap)
        self.assertTrue(bootstrap['chat_id'])

    def test_widget_set_agent_switches_skill_pack(self):
        bootstrap = self.Chat.widget_bootstrap()
        finance = self.Agent.search([('code', '=', 'finance')], limit=1)
        switched = self.Chat.widget_set_agent(bootstrap['chat_id'], finance.id)
        self.assertEqual(switched['agent_id'], finance.id)
        labels = {item['label'] for item in switched['suggestions']}
        self.assertTrue(labels)

    def test_audit_log_stores_agent(self):
        finance = self.Agent.search([('code', '=', 'finance')], limit=1)
        chat = self.Chat.create({'name': 'Audit agent', 'agent_id': finance.id})
        self.Service.process_chat_message(chat, 'Show revenue this month')
        audit = self.env['rn.ai.employee.audit.log'].search([
            ('chat_id', '=', chat.id),
            ('tool_name', '=', 'revenue_this_month'),
        ], limit=1)
        self.assertTrue(audit)
        self.assertEqual(audit.agent_id, finance)

    def test_agent_open_chat_action(self):
        sales = self.Agent.search([('code', '=', 'sales')], limit=1)
        action = sales.action_open_chat()
        chat = self.Chat.browse(action['res_id'])
        self.assertEqual(chat.agent_id, sales)

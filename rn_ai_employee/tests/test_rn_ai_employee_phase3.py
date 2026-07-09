# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'rn_ai_employee')
class TestAiEmployeePhase3(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tool = cls.env['rn.ai.employee.tool']
        cls.Chat = cls.env['rn.ai.employee.chat']
        cls.Service = cls.env['rn.ai.employee.service']
        cls.env['ir.config_parameter'].sudo().set_param('rn_ai_employee.enabled', 'True')
        cls.env['ir.config_parameter'].sudo().set_param(
            'rn_ai_employee.require_write_confirmation', 'True'
        )

    def test_memory_remembers_tool_result(self):
        from ..services.memory_service import get_memory_service

        chat = self.Chat.create({'name': 'Memory test'})
        result = {
            'headline': '3 pending quotations',
            'model': 'sale.order',
            'record_ids': [11, 12, 13],
            'category': 'sales',
        }
        get_memory_service(self.env).remember_tool_result(chat, 'pending_quotations', result)
        self.assertIn('pending_quotations', chat.memory_context)
        self.assertIn('11', chat.memory_context)

    def test_followup_resolves_partner_email_from_memory(self):
        chat = self.Chat.create({'name': 'Follow-up test'})
        chat.write({
            'memory_context': (
                '{"version": 1, "sessions": [{"tool_name": "pending_quotations", '
                '"model": "sale.order", "record_ids": [1, 2, 3], "headline": "3 quotes", '
                '"category": "sales", "at": "2026-01-01"}]}'
            ),
        })
        tool_name, args = self.Service._resolve_tool(chat, 'email the first three customers')
        self.assertEqual(tool_name, 'send_partner_email')
        self.assertEqual(args.get('record_ids'), [1, 2, 3])

    def test_write_action_requires_confirmation(self):
        partner = self.env['res.partner'].create({
            'name': 'Confirm Customer',
            'customer_rank': 1,
        })
        self.env['product.product'].create({
            'name': 'Confirm Product',
            'list_price': 99.0,
            'type': 'consu',
        })
        chat = self.Chat.create({'name': 'Confirm write'})
        self.Service._queue_pending_action(
            chat,
            'create_quotation',
            {
                'partner_name': 'Confirm Customer',
                'product_name': 'Confirm Product',
                'quantity': 1,
            },
            'create quotation',
        )
        pending = self.env['rn.ai.employee.pending.action'].search([
            ('chat_id', '=', chat.id),
            ('state', '=', 'pending'),
        ])
        self.assertTrue(pending)
        self.assertFalse(self.env['sale.order'].search([('partner_id', '=', partner.id)]))
        pending.action_confirm()
        self.assertTrue(self.env['sale.order'].search([('partner_id', '=', partner.id)]))
        audit = self.env['rn.ai.employee.audit.log'].search([
            ('chat_id', '=', chat.id),
            ('tool_name', '=', 'create_quotation'),
            ('result_state', '=', 'success'),
        ])
        self.assertTrue(audit)

    def test_cancel_pending_write(self):
        chat = self.Chat.create({'name': 'Cancel write'})
        self.Service._queue_pending_action(
            chat,
            'send_payment_reminders',
            {'days_overdue': 0, 'limit': 5},
            'send reminders',
        )
        pending = self.env['rn.ai.employee.pending.action'].search([
            ('chat_id', '=', chat.id),
            ('state', '=', 'pending'),
        ], limit=1)
        self.assertTrue(pending)
        pending.action_cancel()
        self.assertEqual(pending.state, 'cancelled')
        cancelled_log = self.env['rn.ai.employee.audit.log'].search([
            ('pending_action_id', '=', pending.id),
            ('result_state', '=', 'cancelled'),
        ])
        self.assertTrue(cancelled_log)

    def test_morning_briefing_tool(self):
        result = self.Tool.execute_by_name('morning_briefing', {})
        self.assertIn('headline', result)
        self.assertIn('Revenue this month', result.get('summary', ''))

    def test_create_rfq_tool(self):
        vendor = self.env['res.partner'].create({
            'name': 'Steel Vendor',
            'supplier_rank': 1,
        })
        self.env['product.product'].create({
            'name': 'Steel Rod',
            'purchase_ok': True,
            'type': 'consu',
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'rn_ai_employee.require_write_confirmation', 'False'
        )
        result = self.Tool.execute_by_name('create_rfq', {
            'vendor_name': 'Steel',
            'product_name': 'Rod',
            'quantity': 2,
        })
        self.assertNotIn('error', result)
        order = self.env['purchase.order'].browse(result['record_ids'])
        self.assertEqual(order.partner_id, vendor)

    def test_audit_log_on_read_tool(self):
        chat = self.Chat.create({'name': 'Audit read'})
        self.Service.process_chat_message(chat, 'Show overdue invoices')
        logs = self.env['rn.ai.employee.audit.log'].search([('chat_id', '=', chat.id)])
        self.assertTrue(logs)
        self.assertEqual(logs[0].result_state, 'success')

    def test_morning_briefing_cron_skips_when_disabled(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'rn_ai_employee.morning_briefing_enabled', 'False'
        )
        before = self.Chat.search_count([('name', 'ilike', 'Morning Briefing')])
        self.Service.cron_morning_briefing()
        after = self.Chat.search_count([('name', 'ilike', 'Morning Briefing')])
        self.assertEqual(before, after)

    def test_morning_briefing_cron_creates_chat_when_enabled(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'rn_ai_employee.morning_briefing_enabled', 'True'
        )
        self.Service.cron_morning_briefing()
        self.assertTrue(self.Chat.search([('name', 'ilike', 'Morning Briefing')], limit=1))

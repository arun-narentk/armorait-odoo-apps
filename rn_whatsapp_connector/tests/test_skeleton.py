# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnWhatsappConnectorPhase1(TransactionCase):
    """Phase 1 tests for ARMORA WhatsApp Automation Platform."""

    def test_security_groups_exist(self):
        group = self.env.ref('rn_whatsapp_connector.group_rn_whatsapp_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_account_and_template_render(self):
        account = self.env['rn.whatsapp.account'].create({
            'name': 'Test Account',
            'provider': 'meta_cloud',
            'phone_number': '+15551234567',
            'simulation_mode': True,
        })
        template = self.env['rn.whatsapp.template'].create({
            'name': 'hello',
            'account_id': account.id,
            'body': 'Hi {{name}}',
            'variable_ids': 'name',
        })
        rendered = self.env['rn.whatsapp.template.service'].render(template, {'name': 'Ada'})
        self.assertEqual(rendered, 'Hi Ada')

    def test_queue_and_simulate_send(self):
        account = self.env['rn.whatsapp.account'].create({
            'name': 'Send Account',
            'provider': 'meta_cloud',
            'simulation_mode': True,
        })
        message = self.env['rn.whatsapp.message.service'].build_text_message(
            account, '+15550002222', 'Test body'
        )
        message.action_queue_message()
        self.assertEqual(message.status, 'queued')
        self.env['rn.whatsapp.message.service'].send_messages(message)
        self.assertEqual(message.status, 'sent')
        self.assertTrue(message.provider_message_id)

    def test_dashboard_payload(self):
        data = self.env['rn.whatsapp.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('queue_size', data['cards'])

    def test_automation_trigger_without_phone_skips(self):
        account = self.env['rn.whatsapp.account'].create({
            'name': 'Auto Account',
            'provider': 'meta_cloud',
            'simulation_mode': True,
        })
        template = self.env['rn.whatsapp.template'].create({
            'name': 'order_ok',
            'account_id': account.id,
            'body': 'Order {{name}}',
            'variable_ids': 'name',
        })
        partner = self.env['res.partner'].create({'name': 'No Phone Partner'})
        rule = self.env['rn.whatsapp.automation.rule'].create({
            'name': 'SO Confirm',
            'trigger': 'sale_order_confirmed',
            'account_id': account.id,
            'template_id': template.id,
            'model_id': self.env.ref('sale.model_sale_order').id,
        })
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
        })
        messages = self.env['rn.whatsapp.automation.service'].run_trigger('sale_order_confirmed', order)
        self.assertFalse(messages)
        self.assertTrue(rule.exists())

# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnAiEmailIntelligence(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env['rn.ai.email.settings'].create({
            'name': 'Test Email AI',
            'company_id': cls.env.company.id,
            'credit_balance': 20,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Email Test Customer',
            'email': 'customer@example.com',
        })
        cls.template = cls.env.ref(
            'rn_ai_email_intelligence.template_sales_followup',
            raise_if_not_found=False,
        )

    def test_groups_exist(self):
        self.assertTrue(self.env.ref('rn_ai_email_intelligence.group_rn_ai_email_user', raise_if_not_found=False))

    def test_context_service_sale(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        order.order_line = [(0, 0, {'name': 'Item', 'product_qty': 1, 'price_unit': 100})]
        ctx = self.env['rn.ai.email.context.service'].build_context(
            partner=self.partner,
            res_model='sale.order',
            res_id=order.id,
        )
        self.assertEqual(ctx['quotation'], order.name)

    def test_generate_sales_draft(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        result = self.env['rn.ai.email.draft.service'].generate_draft(
            partner=self.partner,
            template=self.template,
            res_model='sale.order',
            res_id=order.id,
            tone='professional',
        )
        self.assertIn('quotation', result['subject'].lower() or result['body_html'].lower())
        self.assertTrue(result['context_summary'])

    def test_tone_service(self):
        body = self.env['rn.ai.email.tone.service'].apply_tone('Hello', 'friendly')
        self.assertIn('great day', body)

    def test_dashboard(self):
        data = self.env['rn.ai.email.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)

# -*- coding: utf-8 -*-
"""Tests that validate demo data used for marketplace captures."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_domain_builder')
class TestRnDomainBuilderCaptureData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parser = cls.env['rn.domain.parser.service']
        cls.env.user.group_ids = [
            (4, cls.env.ref('rn_domain_builder.group_rn_domain_builder_manager').id),
        ]

    def test_demo_confirmed_quotations_domain(self):
        result = self.parser.parse('sale.order', 'confirmed quotations')
        self.assertTrue(result['valid'])
        self.assertGreaterEqual(result['record_count'], 0)
        self.assertIn(('state', '=', 'sent'), result['domain'])

    def test_demo_paid_invoices_domain(self):
        result = self.parser.parse('account.move', 'paid invoices this month')
        self.assertTrue(result['valid'])
        self.assertIn(('payment_state', '=', 'paid'), result['domain'])

    def test_builder_action_exists(self):
        action = self.env.ref('rn_domain_builder.action_rn_domain_builder', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.domain.builder')
        launch = self.env.ref('rn_domain_builder.action_rn_domain_builder_launch', raise_if_not_found=False)
        self.assertTrue(launch)

    def test_dictionary_action_exists(self):
        action = self.env.ref('rn_domain_builder.action_rn_domain_dictionary', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.domain.dictionary')

    def test_history_action_exists(self):
        action = self.env.ref('rn_domain_builder.action_rn_domain_history', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.domain.history')

    def test_default_dictionary_loaded(self):
        entries = self.env['rn.domain.dictionary'].search([('active', '=', True)])
        self.assertGreaterEqual(len(entries), 10)
        sale_entries = entries.filtered(lambda row: row.res_model == 'sale.order')
        self.assertGreaterEqual(len(sale_entries), 2)

# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_domain_builder')
class TestRnDomainBuilder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parser = cls.env['rn.domain.parser.service']
        cls.validator = cls.env['rn.domain.validator.service']
        cls.builder = cls.env['rn.domain.builder']
        cls.env.user.group_ids = [
            (4, cls.env.ref('rn_domain_builder.group_rn_domain_builder_manager').id),
        ]

    def test_confirmed_sales_orders(self):
        result = self.parser.parse('sale.order', 'confirmed')
        self.assertTrue(result['valid'])
        self.assertIn(('state', '=', 'sale'), result['domain'])

    def test_confirmed_quotations(self):
        result = self.parser.parse('sale.order', 'confirmed quotations')
        self.assertTrue(result['valid'])
        self.assertIn(('state', '=', 'sent'), result['domain'])

    def test_paid_invoices_this_month(self):
        result = self.parser.parse('account.move', 'paid invoices this month')
        self.assertTrue(result['valid'])
        self.assertIn(('payment_state', '=', 'paid'), result['domain'])
        self.assertTrue(any(
            isinstance(item, tuple) and item[0] == 'invoice_date'
            for item in result['domain']
        ))

    def test_lost_opportunities(self):
        result = self.parser.parse('crm.lead', 'lost')
        self.assertTrue(result['valid'])
        self.assertIn(('active', '=', False), result['domain'])

    def test_products_quantity_below_number(self):
        result = self.parser.parse('product.template', 'quantity below 5')
        self.assertTrue(result['valid'])
        self.assertIn(('qty_available', '<', 5.0), result['domain'])

    def test_paid_invoices_above_amount(self):
        result = self.parser.parse('account.move', 'paid invoices above 10000')
        self.assertTrue(result['valid'])
        self.assertIn(('payment_state', '=', 'paid'), result['domain'])
        self.assertIn(('amount_total', '>', 10000.0), result['domain'])

    def test_or_domain_products(self):
        result = self.parser.parse('product.template', 'archived or quantity below 5')
        self.assertTrue(result['valid'])
        self.assertIn('|', result['domain'])
        self.assertTrue(any(
            isinstance(item, tuple) and item[0] == 'active' and item[2] is False
            for item in result['domain']
        ))

    def test_validator_rejects_invalid_field(self):
        validation = self.validator.validate('sale.order', [('not_a_field', '=', 1)])
        self.assertFalse(validation['valid'])
        self.assertTrue(validation['errors'])

    def test_save_filter_creates_ir_filters(self):
        wizard = self.builder.create({
            'res_model': 'sale.order',
            'description': 'confirmed',
        })
        wizard.action_save_filter()
        filters = self.env['ir.filters'].search([
            ('name', 'ilike', 'confirmed'),
            ('user_ids', 'in', self.env.user.id),
        ])
        self.assertTrue(filters)
        history = self.env['rn.domain.history'].search([
            ('description', '=', 'confirmed'),
            ('user_id', '=', self.env.user.id),
        ], limit=1)
        self.assertTrue(history)
        self.assertTrue(history.filter_id)

    def test_security_groups_exist(self):
        self.assertTrue(self.env.ref('rn_domain_builder.group_rn_domain_builder_user'))
        self.assertTrue(self.env.ref('rn_domain_builder.group_rn_domain_builder_manager'))

    def test_suggestions_return_chips(self):
        suggestions = self.parser.suggest_for_partial('sale.order', 'con')
        self.assertIn('confirmed', suggestions)

    def test_dictionary_configuration_create(self):
        entry = self.env['rn.domain.dictionary'].create({
            'name': 'VIP Sales Marker',
            'res_model': 'sale.order',
            'trigger_word': 'priority',
            'field_name': 'state',
            'operator': '=',
            'value_type': 'char',
            'value_char': 'sale',
        })
        result = self.parser.parse('sale.order', 'priority')
        self.assertIn(('state', '=', 'sale'), result['domain'])
        entry.unlink()

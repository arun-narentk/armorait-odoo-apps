# -*- coding: utf-8 -*-
"""Tests for Customer Outstanding on Sale Order."""

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_customer_outstanding_sale_order')
class TestCustomerOutstandingSaleOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Outstanding Customer A',
            'company_id': False,
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'Outstanding Customer B',
            'company_id': False,
        })
        cls.contact_a = cls.env['res.partner'].create({
            'name': 'Contact of A',
            'parent_id': cls.partner_a.id,
            'type': 'contact',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Outstanding Test Product',
            'list_price': 100.0,
            'type': 'consu',
            'sale_ok': True,
            'taxes_id': [Command.clear()],
        })
        cls.income_account = cls.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_ids', 'in', cls.company.id),
        ], limit=1)
        if not cls.income_account:
            cls.income_account = cls.env['account.account'].search([
                ('account_type', '=', 'income'),
            ], limit=1)
        cls.sale_journal = cls.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', cls.company.id),
        ], limit=1)

    def _create_sale_order(self, partner):
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'company_id': self.company.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 10.0,
                }),
            ],
        })

    def _create_customer_invoice(self, partner, amount, post=False, move_type='out_invoice'):
        self.assertTrue(self.sale_journal, 'Sale journal is required for tests')
        self.assertTrue(self.income_account, 'Income account is required for tests')
        move = self.env['account.move'].with_company(self.company).create({
            'move_type': move_type,
            'partner_id': partner.id,
            'company_id': self.company.id,
            'journal_id': self.sale_journal.id,
            'invoice_date': fields.Date.from_string('2026-03-01'),
            'invoice_line_ids': [
                Command.create({
                    'name': 'Outstanding line',
                    'quantity': 1,
                    'price_unit': amount,
                    'account_id': self.income_account.id,
                    'tax_ids': [Command.clear()],
                }),
            ],
        })
        if post:
            move.action_post()
            self.env.invalidate_all()
        return move

    def _pay_invoice(self, move, amount):
        self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=move.ids,
        ).with_company(self.company).create({
            'amount': amount,
            'currency_id': move.currency_id.id,
        })._create_payments()
        self.env.invalidate_all()

    def _refresh_outstanding(self, order):
        order.invalidate_recordset(['customer_outstanding', 'has_customer_outstanding'])
        order._compute_customer_outstanding()
        return order.customer_outstanding

    def test_01_no_outstanding(self):
        order = self._create_sale_order(self.partner_a)
        self.assertEqual(order.customer_outstanding, 0.0)
        self.assertFalse(order.has_customer_outstanding)

    def test_02_one_unpaid_posted_invoice(self):
        invoice = self._create_customer_invoice(self.partner_a, 1250.0, post=True)
        order = self._create_sale_order(self.partner_a)
        outstanding = self._refresh_outstanding(order)
        self.assertEqual(outstanding, invoice.amount_residual)
        self.assertTrue(order.has_customer_outstanding)

    def test_03_multiple_unpaid_invoices(self):
        inv1 = self._create_customer_invoice(self.partner_a, 400.0, post=True)
        inv2 = self._create_customer_invoice(self.partner_a, 600.0, post=True)
        order = self._create_sale_order(self.partner_a)
        outstanding = self._refresh_outstanding(order)
        expected = inv1.amount_residual + inv2.amount_residual
        self.assertEqual(outstanding, expected)

    def test_04_partial_payment(self):
        invoice = self._create_customer_invoice(self.partner_a, 1000.0, post=True)
        self._pay_invoice(invoice, 300.0)
        order = self._create_sale_order(self.partner_a)
        outstanding = self._refresh_outstanding(order)
        self.assertEqual(outstanding, invoice.amount_residual)
        self.assertEqual(outstanding, 700.0)

    def test_05_full_payment_clears_outstanding(self):
        invoice = self._create_customer_invoice(self.partner_a, 500.0, post=True)
        self._pay_invoice(invoice, invoice.amount_residual)
        order = self._create_sale_order(self.partner_a)
        outstanding = self._refresh_outstanding(order)
        self.assertEqual(outstanding, 0.0)
        self.assertFalse(order.has_customer_outstanding)

    def test_06_credit_note_reduces_outstanding(self):
        self._create_customer_invoice(self.partner_a, 800.0, post=True)
        self._create_customer_invoice(
            self.partner_a, 200.0, post=True, move_type='out_refund',
        )
        order = self._create_sale_order(self.partner_a)
        outstanding = self._refresh_outstanding(order)
        # partner.credit nets invoice receivable and credit-note residual
        partner_credit = (
            self.partner_a.with_company(self.company).sudo().credit or 0.0
        )
        self.assertEqual(outstanding, partner_credit)
        self.assertEqual(outstanding, 600.0)

    def test_07_changing_customer_updates_outstanding(self):
        self._create_customer_invoice(self.partner_a, 350.0, post=True)
        self._create_customer_invoice(self.partner_b, 900.0, post=True)
        order = self._create_sale_order(self.partner_a)
        self.assertEqual(self._refresh_outstanding(order), 350.0)
        order.partner_id = self.partner_b
        self.assertEqual(self._refresh_outstanding(order), 900.0)

    def test_08_draft_and_cancelled_ignored(self):
        draft = self._create_customer_invoice(self.partner_a, 777.0, post=False)
        self.assertEqual(draft.state, 'draft')
        cancelled = self._create_customer_invoice(self.partner_a, 888.0, post=True)
        cancelled.button_cancel()
        self.env.invalidate_all()
        order = self._create_sale_order(self.partner_a)
        outstanding = self._refresh_outstanding(order)
        self.assertEqual(outstanding, 0.0)
        self.assertFalse(order.has_customer_outstanding)

    def test_09_commercial_partner_from_contact(self):
        self._create_customer_invoice(self.partner_a, 450.0, post=True)
        order = self._create_sale_order(self.contact_a)
        outstanding = self._refresh_outstanding(order)
        self.assertEqual(outstanding, 450.0)
        self.assertTrue(order.has_customer_outstanding)

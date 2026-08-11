# -*- coding: utf-8 -*-
"""Tests for Sale Order Customer Previous Price."""

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_sale_order_customer_previous_price')
class TestSaleOrderCustomerPreviousPrice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'PrevPrice Customer',
            'company_id': False,
        })
        cls.contact = cls.env['res.partner'].create({
            'name': 'Purchase Department',
            'parent_id': cls.partner.id,
            'type': 'contact',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'PrevPrice Product',
            'list_price': 100.0,
            'type': 'consu',
            'sale_ok': True,
        })
        cls.other_product = cls.env['product.product'].create({
            'name': 'Other PrevPrice Product',
            'list_price': 50.0,
            'type': 'consu',
            'sale_ok': True,
        })
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id

    def _create_order(self, partner, product, price_unit, confirm=False, date_order=None, pricelist=None):
        vals = {
            'partner_id': partner.id,
            'company_id': self.company.id,
            'date_order': date_order or fields.Datetime.now(),
            'order_line': [
                Command.create({
                    'product_id': product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': price_unit,
                }),
            ],
        }
        if pricelist:
            vals['pricelist_id'] = pricelist.id
        order = self.env['sale.order'].create(vals)
        if confirm:
            order.action_confirm()
        return order

    def test_01_no_previous_order(self):
        order = self._create_order(self.partner, self.product, 1050.0)
        line = order.order_line[0]
        self.assertFalse(line.previous_customer_price)
        self.assertFalse(line.previous_customer_order_id)

    def test_02_one_confirmed_previous_order(self):
        previous = self._create_order(self.partner, self.product, 900.0, confirm=True)
        current = self._create_order(self.partner, self.product, 1050.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_customer_price, 900.0)
        self.assertEqual(line.previous_customer_order_id, previous)
        self.assertEqual(line.previous_customer_price_difference, 150.0)

    def test_03_multiple_previous_orders_use_latest(self):
        older = self._create_order(self.partner, self.product, 800.0, confirm=True)
        older.write({'date_order': '2026-01-01 10:00:00'})
        latest = self._create_order(self.partner, self.product, 920.0, confirm=True)
        latest.write({'date_order': '2026-06-01 10:00:00'})
        current = self._create_order(self.partner, self.product, 1000.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_customer_price, 920.0)
        self.assertEqual(line.previous_customer_order_id, latest)

    def test_04_cancelled_previous_order_ignored(self):
        cancelled = self._create_order(self.partner, self.product, 700.0, confirm=True)
        cancelled._action_cancel()
        current = self._create_order(self.partner, self.product, 1000.0)
        line = current.order_line[0]
        self.assertFalse(line.previous_customer_price)
        self.assertFalse(line.previous_customer_order_id)

    def test_05_different_product_ignored(self):
        self._create_order(self.partner, self.other_product, 400.0, confirm=True)
        current = self._create_order(self.partner, self.product, 1000.0)
        self.assertFalse(current.order_line[0].previous_customer_price)

    def test_06_current_order_excluded(self):
        order = self._create_order(self.partner, self.product, 1111.0, confirm=True)
        line = order.order_line[0]
        self.assertFalse(line.previous_customer_price)

    def test_07_commercial_partner_contact(self):
        previous = self._create_order(self.partner, self.product, 880.0, confirm=True)
        current = self._create_order(self.contact, self.product, 1000.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_customer_price, 880.0)
        self.assertEqual(line.previous_customer_order_id, previous)

    def test_08_currency_conversion(self):
        other_currency = self.env['res.currency'].with_context(active_test=False).search([
            ('id', '!=', self.currency.id),
        ], limit=1)
        if not other_currency:
            self.skipTest('Need a second currency')
        other_currency.active = True

        rate_date = fields.Date.from_string('2026-03-01')
        self.env['res.currency.rate'].search([
            ('currency_id', '=', other_currency.id),
            ('name', '=', rate_date),
            ('company_id', '=', self.company.id),
        ]).unlink()
        self.env['res.currency.rate'].create({
            'name': rate_date,
            'currency_id': other_currency.id,
            'rate': 2.0,
            'company_id': self.company.id,
        })

        foreign_pricelist = self.env['product.pricelist'].create({
            'name': 'PrevPrice Foreign',
            'currency_id': other_currency.id,
            'company_id': self.company.id,
        })
        previous = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'pricelist_id': foreign_pricelist.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 100.0,
                }),
            ],
        })
        previous.action_confirm()
        previous.write({'date_order': '2026-03-01 12:00:00'})
        self.assertEqual(previous.currency_id, other_currency)

        current = self._create_order(self.partner, self.product, 60.0)
        line = current.order_line[0]
        expected = other_currency._convert(
            100.0,
            self.currency,
            self.company,
            rate_date,
        )
        self.assertAlmostEqual(line.previous_customer_price, expected, places=2)
        self.assertEqual(line.previous_customer_order_id, previous)

    def test_09_product_change_recomputes(self):
        self._create_order(self.partner, self.product, 910.0, confirm=True)
        self._create_order(self.partner, self.other_product, 450.0, confirm=True)
        current = self._create_order(self.partner, self.product, 1000.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_customer_price, 910.0)
        line.product_id = self.other_product
        self.assertEqual(line.previous_customer_price, 450.0)

    def test_10_customer_change_recomputes(self):
        other_partner = self.env['res.partner'].create({'name': 'Other PrevPrice Customer'})
        self._create_order(self.partner, self.product, 930.0, confirm=True)
        self._create_order(other_partner, self.product, 500.0, confirm=True)
        current = self._create_order(self.partner, self.product, 1000.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_customer_price, 930.0)
        current.partner_id = other_partner
        self.assertEqual(line.previous_customer_price, 500.0)

    def test_11_difference_percentage_and_zero_safe(self):
        self._create_order(self.partner, self.product, 0.0, confirm=True)
        current = self._create_order(self.partner, self.product, 10.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_customer_price, 0.0)
        self.assertEqual(line.previous_customer_price_difference, 10.0)
        self.assertFalse(line.previous_customer_price_percentage)

    def test_12_draft_previous_order_ignored(self):
        self._create_order(self.partner, self.product, 777.0, confirm=False)
        current = self._create_order(self.partner, self.product, 1000.0)
        self.assertFalse(current.order_line[0].previous_customer_price)

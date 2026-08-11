# -*- coding: utf-8 -*-
"""Tests for Product Last Sale Price."""

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_product_last_sale_price')
class TestProductLastSalePrice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'LastSale Customer A',
            'company_id': False,
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'LastSale Customer B',
            'company_id': False,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'LastSale Product A',
            'list_price': 999.0,
            'type': 'consu',
            'sale_ok': True,
            'taxes_id': [Command.clear()],
        })
        cls.other_product = cls.env['product.product'].create({
            'name': 'LastSale Product B',
            'list_price': 50.0,
            'type': 'consu',
            'sale_ok': True,
            'taxes_id': [Command.clear()],
        })

    def _create_order(
        self,
        partner,
        product,
        price_unit,
        confirm=False,
        date_order=None,
        discount=0.0,
        company=None,
    ):
        company = company or self.company
        order = self.env['sale.order'].with_company(company).create({
            'partner_id': partner.id,
            'company_id': company.id,
            'date_order': date_order or fields.Datetime.now(),
            'order_line': [
                Command.create({
                    'product_id': product.id,
                    'product_uom_qty': 1.0,
                    'price_unit': price_unit,
                    'discount': discount,
                }),
            ],
        })
        if confirm:
            order.action_confirm()
        return order

    def test_01_no_previous_sale(self):
        order = self._create_order(self.partner_a, self.product, 1050.0)
        self.assertEqual(order.order_line[0].last_sale_price, 0.0)

    def test_02_one_previous_sale(self):
        self._create_order(self.partner_a, self.product, 100.0, confirm=True)
        current = self._create_order(self.partner_a, self.product, 120.0)
        self.assertEqual(current.order_line[0].last_sale_price, 100.0)

    def test_03_multiple_historical_use_latest(self):
        so1 = self._create_order(self.partner_a, self.product, 100.0, confirm=True)
        so1.write({'date_order': '2026-01-10 10:00:00'})
        so2 = self._create_order(self.partner_a, self.product, 125.0, confirm=True)
        so2.write({'date_order': '2026-03-15 10:00:00'})
        so3 = self._create_order(self.partner_a, self.product, 110.0, confirm=True)
        so3.write({'date_order': '2026-05-20 10:00:00'})
        current = self._create_order(self.partner_a, self.product, 130.0)
        self.assertEqual(current.order_line[0].last_sale_price, 110.0)

    def test_04_different_customer(self):
        self._create_order(self.partner_a, self.product, 100.0, confirm=True)
        current = self._create_order(self.partner_b, self.product, 120.0)
        self.assertEqual(current.order_line[0].last_sale_price, 0.0)

    def test_05_cancelled_order_ignored(self):
        cancelled = self._create_order(self.partner_a, self.product, 999.0, confirm=True)
        cancelled._action_cancel()
        current = self._create_order(self.partner_a, self.product, 120.0)
        self.assertEqual(current.order_line[0].last_sale_price, 0.0)

    def test_06_draft_quotation_ignored(self):
        self._create_order(self.partner_a, self.product, 999.0, confirm=False)
        current = self._create_order(self.partner_a, self.product, 120.0)
        self.assertEqual(current.order_line[0].last_sale_price, 0.0)

    def test_07_discount_effective_price(self):
        self._create_order(
            self.partner_a, self.product, 100.0, confirm=True, discount=10.0,
        )
        current = self._create_order(self.partner_a, self.product, 120.0)
        self.assertEqual(current.order_line[0].last_sale_price, 90.0)

    def test_08_current_order_excluded(self):
        order = self._create_order(self.partner_a, self.product, 900.0, confirm=True)
        # Confirmed current order must not use itself as history for its own line.
        self.assertEqual(order.order_line[0].last_sale_price, 0.0)
        # A second draft order should see the confirmed one.
        draft = self._create_order(self.partner_a, self.product, 950.0)
        self.assertEqual(draft.order_line[0].last_sale_price, 900.0)

    def test_09_multi_company(self):
        other_company = self.env['res.company'].search([
            ('id', '!=', self.company.id),
        ], limit=1)
        if not other_company:
            self.skipTest('Need a second company already present in the database')

        self._create_order(
            self.partner_a, self.product, 60.0, confirm=True, company=self.company,
        )
        try:
            self._create_order(
                self.partner_a, self.product, 200.0, confirm=True, company=other_company,
            )
        except Exception:
            self.skipTest('Could not create a sale order in the second company')

        current = self._create_order(
            self.partner_a, self.product, 70.0, company=self.company,
        )
        self.assertEqual(current.order_line[0].last_sale_price, 60.0)

    def test_10_customer_and_product_change(self):
        self._create_order(self.partner_a, self.product, 100.0, confirm=True)
        self._create_order(self.partner_b, self.product, 550.0, confirm=True)
        self._create_order(self.partner_a, self.other_product, 40.0, confirm=True)

        order = self._create_order(self.partner_a, self.product, 120.0)
        line = order.order_line[0]
        self.assertEqual(line.last_sale_price, 100.0)

        order.partner_id = self.partner_b
        line.invalidate_recordset(['last_sale_price'])
        line._compute_last_sale_price()
        self.assertEqual(line.last_sale_price, 550.0)

        line.product_id = self.other_product
        line.invalidate_recordset(['last_sale_price'])
        line._compute_last_sale_price()
        self.assertEqual(line.last_sale_price, 0.0)

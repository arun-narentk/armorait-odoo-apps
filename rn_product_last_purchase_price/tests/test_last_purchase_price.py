# -*- coding: utf-8 -*-
"""Tests for Product Last Purchase Price."""

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_product_last_purchase_price')
class TestProductLastPurchasePrice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.vendor_a = cls.env['res.partner'].create({
            'name': 'LastPrice Vendor A',
            'supplier_rank': 1,
            'company_id': False,
        })
        cls.vendor_b = cls.env['res.partner'].create({
            'name': 'LastPrice Vendor B',
            'supplier_rank': 1,
            'company_id': False,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'LastPrice Product',
            'type': 'consu',
            'purchase_ok': True,
            'list_price': 100.0,
        })
        cls.other_product = cls.env['product.product'].create({
            'name': 'Other LastPrice Product',
            'type': 'consu',
            'purchase_ok': True,
        })

    def _create_po(self, vendor, product, price_unit, confirm=False, company=None):
        company = company or self.company
        order = self.env['purchase.order'].with_company(company).create({
            'partner_id': vendor.id,
            'company_id': company.id,
            'order_line': [
                Command.create({
                    'product_id': product.id,
                    'name': product.display_name,
                    'product_qty': 1.0,
                    'price_unit': price_unit,
                    'product_uom_id': product.uom_id.id,
                    'date_planned': fields.Datetime.now(),
                }),
            ],
        })
        if confirm:
            order.button_confirm()
        return order

    def test_01_first_purchase_no_previous_on_line(self):
        po = self._create_po(self.vendor_a, self.product, 100.0)
        line = po.order_line[0]
        self.assertFalse(line.last_purchase_order_id)
        self.assertEqual(line.last_purchase_price, 0.0)
        self.assertFalse(line.purchase_price_difference)

    def test_02_first_purchase_updates_product(self):
        po = self._create_po(self.vendor_a, self.product, 100.0, confirm=True)
        product = self.product.with_company(self.company)
        self.assertEqual(product.last_purchase_price, 100.0)
        self.assertEqual(product.last_purchase_order_id, po)
        self.assertEqual(product.last_purchase_vendor_id, self.vendor_a)
        self.assertTrue(product.last_purchase_date)

    def test_03_second_purchase_line_shows_previous(self):
        previous = self._create_po(self.vendor_a, self.product, 100.0, confirm=True)
        current = self._create_po(self.vendor_a, self.product, 125.0)
        line = current.order_line[0]
        self.assertEqual(line.last_purchase_price, 100.0)
        self.assertEqual(line.last_purchase_order_id, previous)
        self.assertEqual(line.purchase_price_difference, 25.0)
        self.assertEqual(line.purchase_price_difference_percent, 25.0)
        self.assertTrue(line.has_last_purchase_price_increase)
        self.assertIn('increased', (line.last_purchase_warning or '').lower())

    def test_04_price_decrease_warning(self):
        self._create_po(self.vendor_a, self.product, 100.0, confirm=True)
        current = self._create_po(self.vendor_a, self.product, 90.0)
        line = current.order_line[0]
        self.assertEqual(line.purchase_price_difference, -10.0)
        self.assertEqual(line.purchase_price_difference_percent, -10.0)
        self.assertFalse(line.has_last_purchase_price_increase)
        self.assertIn('reduced', (line.last_purchase_warning or '').lower())

    def test_05_vendor_specific_then_fallback(self):
        from_a = self._create_po(self.vendor_a, self.product, 80.0, confirm=True)
        from_b = self._create_po(self.vendor_b, self.product, 95.0, confirm=True)
        # Same vendor A: prefer A's previous (80), not B's 95
        current_a = self._create_po(self.vendor_a, self.product, 110.0)
        self.assertEqual(current_a.order_line[0].last_purchase_price, 80.0)
        self.assertEqual(current_a.order_line[0].last_purchase_order_id, from_a)
        # New vendor with no history: fallback to latest any vendor (B @ 95 if newer)
        other_vendor = self.env['res.partner'].create({
            'name': 'LastPrice Vendor C',
            'supplier_rank': 1,
        })
        current_c = self._create_po(other_vendor, self.product, 120.0)
        self.assertEqual(current_c.order_line[0].last_purchase_order_id, from_b)
        self.assertEqual(current_c.order_line[0].last_purchase_price, 95.0)

    def test_06_cancelled_purchase_ignored(self):
        confirmed = self._create_po(self.vendor_a, self.product, 70.0, confirm=True)
        cancelled = self._create_po(self.vendor_a, self.product, 999.0, confirm=True)
        cancelled.button_cancel()
        current = self._create_po(self.vendor_a, self.product, 75.0)
        line = current.order_line[0]
        self.assertEqual(line.last_purchase_price, 70.0)
        self.assertEqual(line.last_purchase_order_id, confirmed)
        product = self.product.with_company(self.company)
        self.assertEqual(product.last_purchase_order_id, confirmed)
        self.assertEqual(product.last_purchase_price, 70.0)

    def test_07_draft_purchase_ignored_for_product(self):
        self._create_po(self.vendor_a, self.product, 55.0, confirm=False)
        product = self.product.with_company(self.company)
        self.assertFalse(product.last_purchase_order_id)
        self.assertEqual(product.last_purchase_price, 0.0)

    def test_08_product_variants(self):
        attribute = self.env['product.attribute'].create({
            'name': 'LastPrice Color',
            'create_variant': 'always',
            'value_ids': [
                Command.create({'name': 'White LP'}),
                Command.create({'name': 'Black LP'}),
            ],
        })
        template = self.env['product.template'].create({
            'name': 'LastPrice Variant Template',
            'purchase_ok': True,
            'type': 'consu',
            'attribute_line_ids': [
                Command.create({
                    'attribute_id': attribute.id,
                    'value_ids': [Command.set(attribute.value_ids.ids)],
                }),
            ],
        })
        variants = template.product_variant_ids
        self.assertGreaterEqual(len(variants), 2)
        white = variants[0]
        black = variants[1]
        po = self._create_po(self.vendor_a, white, 40.0, confirm=True)
        white = white.with_company(self.company)
        black = black.with_company(self.company)
        self.assertEqual(white.last_purchase_price, 40.0)
        self.assertEqual(white.last_purchase_order_id, po)
        self.assertFalse(black.last_purchase_order_id)
        template.invalidate_recordset()
        self.assertEqual(template.last_purchase_order_id, po)
        self.assertEqual(template.last_purchase_price, 40.0)

    def test_09_multi_company(self):
        other_company = self.env['res.company'].search([
            ('id', '!=', self.company.id),
        ], limit=1)
        if not other_company:
            self.skipTest('Need a second company already present in the database')
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', other_company.id),
        ], limit=1)
        if not picking_type:
            self.skipTest('Second company has no incoming picking type')

        self._create_po(self.vendor_a, self.product, 60.0, confirm=True, company=self.company)
        order = self.env['purchase.order'].with_company(other_company).create({
            'partner_id': self.vendor_a.id,
            'company_id': other_company.id,
            'picking_type_id': picking_type.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'name': self.product.display_name,
                    'product_qty': 1.0,
                    'price_unit': 200.0,
                    'product_uom_id': self.product.uom_id.id,
                    'date_planned': fields.Datetime.now(),
                }),
            ],
        })
        order.button_confirm()

        in_main = self.product.with_company(self.company)
        in_other = self.product.with_company(other_company)
        self.assertEqual(in_main.last_purchase_price, 60.0)
        self.assertEqual(in_other.last_purchase_price, 200.0)

        current = self._create_po(self.vendor_a, self.product, 70.0, company=self.company)
        self.assertEqual(current.order_line[0].last_purchase_price, 60.0)

    def test_10_second_confirm_updates_product_fields(self):
        first = self._create_po(self.vendor_a, self.product, 100.0, confirm=True)
        second = self._create_po(self.vendor_a, self.product, 130.0, confirm=True)
        product = self.product.with_company(self.company)
        self.assertEqual(product.last_purchase_price, 130.0)
        self.assertEqual(product.last_purchase_order_id, second)
        self.assertNotEqual(product.last_purchase_order_id, first)

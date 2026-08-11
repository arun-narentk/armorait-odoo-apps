# -*- coding: utf-8 -*-
"""Tests for Purchase Vendor Previous Price."""

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_purchase_vendor_previous_price')
class TestPurchaseVendorPreviousPrice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id
        cls.vendor = cls.env['res.partner'].create({
            'name': 'PrevVendor Supplier',
            'company_id': False,
            'supplier_rank': 1,
        })
        cls.vendor_contact = cls.env['res.partner'].create({
            'name': 'Sales Desk',
            'parent_id': cls.vendor.id,
            'type': 'contact',
        })
        cls.other_vendor = cls.env['res.partner'].create({
            'name': 'Other PrevVendor Supplier',
            'company_id': False,
            'supplier_rank': 1,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'PrevVendor Product',
            'type': 'consu',
            'purchase_ok': True,
            'list_price': 100.0,
            'standard_price': 80.0,
        })
        cls.other_product = cls.env['product.product'].create({
            'name': 'Other PrevVendor Product',
            'type': 'consu',
            'purchase_ok': True,
            'list_price': 40.0,
            'standard_price': 30.0,
        })

    def _create_po(self, vendor, product, price_unit, confirm=False, product_uom=None):
        vals = {
            'partner_id': vendor.id,
            'company_id': self.company.id,
            'order_line': [
                Command.create({
                    'product_id': product.id,
                    'name': product.display_name,
                    'product_qty': 1.0,
                    'price_unit': price_unit,
                    'product_uom_id': (product_uom or product.uom_id).id,
                    'date_planned': fields.Datetime.now(),
                }),
            ],
        }
        order = self.env['purchase.order'].create(vals)
        if confirm:
            order.button_confirm()
        return order

    def test_01_no_previous_purchase(self):
        po = self._create_po(self.vendor, self.product, 55.0)
        self.assertEqual(po.order_line[0].previous_vendor_price, 0.0)
        self.assertFalse(po.order_line[0].previous_vendor_order_id)

    def test_02_one_previous_purchase(self):
        previous = self._create_po(self.vendor, self.product, 42.0, confirm=True)
        current = self._create_po(self.vendor, self.product, 50.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_vendor_price, 42.0)
        self.assertEqual(line.previous_vendor_order_id, previous)
        self.assertTrue(line.previous_vendor_price_date)

    def test_03_multiple_previous_use_latest(self):
        older = self._create_po(self.vendor, self.product, 30.0, confirm=True)
        older.write({'date_approve': '2026-01-01 10:00:00'})
        latest = self._create_po(self.vendor, self.product, 48.0, confirm=True)
        latest.write({'date_approve': '2026-06-01 10:00:00'})
        current = self._create_po(self.vendor, self.product, 55.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_vendor_price, 48.0)
        self.assertEqual(line.previous_vendor_order_id, latest)

    def test_04_current_po_ignored(self):
        po = self._create_po(self.vendor, self.product, 77.0, confirm=True)
        self.assertEqual(po.order_line[0].previous_vendor_price, 0.0)

    def test_05_cancelled_ignored(self):
        cancelled = self._create_po(self.vendor, self.product, 33.0, confirm=True)
        cancelled.button_cancel()
        current = self._create_po(self.vendor, self.product, 50.0)
        self.assertEqual(current.order_line[0].previous_vendor_price, 0.0)

    def test_06_draft_rfq_ignored(self):
        self._create_po(self.vendor, self.product, 39.0, confirm=False)
        current = self._create_po(self.vendor, self.product, 50.0)
        self.assertEqual(current.order_line[0].previous_vendor_price, 0.0)

    def test_07_different_vendor_ignored(self):
        self._create_po(self.other_vendor, self.product, 21.0, confirm=True)
        current = self._create_po(self.vendor, self.product, 50.0)
        self.assertEqual(current.order_line[0].previous_vendor_price, 0.0)

    def test_08_different_product_ignored(self):
        self._create_po(self.vendor, self.other_product, 18.0, confirm=True)
        current = self._create_po(self.vendor, self.product, 50.0)
        self.assertEqual(current.order_line[0].previous_vendor_price, 0.0)

    def test_09_vendor_and_product_change_recompute(self):
        self._create_po(self.vendor, self.product, 44.0, confirm=True)
        self._create_po(self.other_vendor, self.other_product, 19.0, confirm=True)
        current = self._create_po(self.vendor, self.product, 50.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_vendor_price, 44.0)

        line.product_id = self.other_product
        line.product_uom_id = self.other_product.uom_id
        self.assertEqual(line.previous_vendor_price, 0.0)

        current.partner_id = self.other_vendor
        line.invalidate_recordset()
        self.assertEqual(line.previous_vendor_price, 19.0)

    def test_10_currency_conversion(self):
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

        previous = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'company_id': self.company.id,
            'currency_id': other_currency.id,
            'order_line': [
                Command.create({
                    'product_id': self.product.id,
                    'name': self.product.display_name,
                    'product_qty': 1.0,
                    'price_unit': 100.0,
                    'product_uom_id': self.product.uom_id.id,
                    'date_planned': fields.Datetime.now(),
                }),
            ],
        })
        previous.button_confirm()
        previous.write({'date_approve': '2026-03-01 12:00:00'})

        current = self._create_po(self.vendor, self.product, 60.0)
        line = current.order_line[0]
        expected = other_currency._convert(
            100.0,
            self.currency,
            self.company,
            rate_date,
        )
        self.assertAlmostEqual(line.previous_vendor_price, expected, places=2)
        self.assertEqual(line.previous_vendor_order_id, previous)

    def test_11_commercial_partner_contact(self):
        previous = self._create_po(self.vendor, self.product, 41.0, confirm=True)
        current = self._create_po(self.vendor_contact, self.product, 50.0)
        line = current.order_line[0]
        self.assertEqual(line.previous_vendor_price, 41.0)
        self.assertEqual(line.previous_vendor_order_id, previous)

    def test_12_uom_price_conversion(self):
        base_uom = self.product.uom_id
        related_uom = base_uom.related_uom_ids[:1]
        if not related_uom:
            related_uom = self.env['uom.uom'].create({
                'name': 'PrevVendor Pack10',
                'relative_uom_id': base_uom.id,
                'relative_factor': 10.0,
            })

        previous = self._create_po(
            self.vendor,
            self.product,
            100.0,
            confirm=True,
            product_uom=related_uom,
        )
        current = self._create_po(self.vendor, self.product, 10.0)
        expected = related_uom._compute_price(100.0, base_uom)
        expected = self.currency.round(expected)
        self.assertAlmostEqual(current.order_line[0].previous_vendor_price, expected, places=2)
        self.assertEqual(current.order_line[0].previous_vendor_order_id, previous)

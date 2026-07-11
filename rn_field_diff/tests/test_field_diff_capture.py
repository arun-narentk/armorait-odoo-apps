# -*- coding: utf-8 -*-
"""Tests for demo data and actions used in marketplace captures."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_field_diff_capture')
class TestRnFieldDiffCaptureData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env.ref('rn_field_diff.demo_field_diff_partner_a')
        cls.partner_b = cls.env.ref('rn_field_diff.demo_field_diff_partner_b')
        cls.product = cls.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner_a.id,
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1})],
        })
        cls.env.flush_all()
        cls.cr.flush()
        cls.order.write({'partner_id': cls.partner_b.id})
        cls.env.flush_all()
        cls.cr.flush()

    def _flush_tracking(self):
        self.env.flush_all()
        self.cr.flush()

    def test_capture_order_has_field_diff(self):
        diffs = self.env['rn.field.diff'].search([
            ('model', '=', 'sale.order'),
            ('res_id', '=', self.order.id),
        ])
        self.assertTrue(diffs)

    def test_field_diff_action_exists(self):
        action = self.env.ref('rn_field_diff.action_rn_field_diff', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.field.diff')

    def test_history_button_action(self):
        action = self.order.action_view_field_diff_history()
        self.assertEqual(action['res_model'], 'rn.field.diff')

    def test_export_wizard_model_exists(self):
        self.assertIn('rn.field.diff.export.wizard', self.env)

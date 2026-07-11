# -*- coding: utf-8 -*-
"""Tests for demo data and actions used in live marketplace captures."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_visual_enhancer_capture')
class TestRnSmartColorTagsCaptureData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        if not cls.product:
            cls.product = cls.env['product.product'].create({
                'name': 'Visual Enhancer Capture Product',
                'type': 'consu',
                'list_price': 10.0,
                'sale_ok': True,
            })
        cls.partner = cls.env['res.partner'].create({
            'name': 'COLORTAG Capture Customer',
            'email': 'colortag.capture@armorait.com',
        })
        cls.order = cls.env['sale.order'].with_context(rn_skip_color_refresh=True).create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1})],
        })

    def test_capture_sale_order_has_tag(self):
        self.order._rn_refresh_color_tags()
        self.assertTrue(self.order.rn_color_tag_label)
        self.assertTrue(self.order.rn_color_tag_color)

    def test_color_rules_action_exists(self):
        action = self.env.ref('rn_visual_enhancer.action_rn_color_rule', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.color.rule')

    def test_default_sale_rules_loaded(self):
        rules = self.env['rn.color.rule'].search([
            ('model_name', '=', 'sale.order'),
            ('active', '=', True),
        ])
        self.assertGreaterEqual(len(rules), 1)

    def test_service_tags_for_capture_order(self):
        payload = self.env['rn.color.rule.service'].get_tags_batch(
            'sale.order', [self.order.id],
        )
        self.assertTrue(payload[self.order.id].get('label'))

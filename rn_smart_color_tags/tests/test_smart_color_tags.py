# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnSmartColorTags(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        cls.partner = cls.env['res.partner'].create({'name': 'COLORTAG Test Partner'})
        cls.rule_confirmed = cls.env['rn.color.rule'].with_context(rn_skip_color_recompute=True).create({
            'name': 'Test Confirmed SO',
            'model_id': cls.env.ref('sale.model_sale_order').id,
            'domain': "[('partner_id.name', 'ilike', 'COLORTAG%'), ('state', '=', 'sale')]",
            'color': 'green',
            'priority': 200,
            'label': 'CONFIRMED',
            'icon': 'check',
        })
        cls.rule_draft = cls.env['rn.color.rule'].with_context(rn_skip_color_recompute=True).create({
            'name': 'Test Draft SO',
            'model_id': cls.env.ref('sale.model_sale_order').id,
            'domain': "[('partner_id.name', 'ilike', 'COLORTAG%'), ('state', '=', 'draft')]",
            'color': 'gray',
            'priority': 200,
            'label': 'DRAFT',
            'icon': 'clock',
        })
        cls.order_draft = cls.env['sale.order'].with_context(rn_skip_color_refresh=True).create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1})],
        })

    def _create_confirmed_order(self):
        order = self.env['sale.order'].with_context(rn_skip_color_refresh=True).create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {'product_id': self.product.id, 'product_uom_qty': 1})],
        })
        order.with_context(rn_skip_color_refresh=True).action_confirm()
        order._rn_refresh_color_tags()
        return order

    def test_higher_priority_rule_wins(self):
        order = self._create_confirmed_order()
        service = self.env['rn.color.rule.service']
        tag = service.get_tags_batch('sale.order', [order.id])
        self.assertEqual(tag[order.id]['color'], 'green')
        self.assertEqual(tag[order.id]['label'], 'CONFIRMED')

    def test_draft_order_gets_gray_tag(self):
        service = self.env['rn.color.rule.service']
        tag = service.get_tags_batch('sale.order', [self.order_draft.id])
        self.assertEqual(tag[self.order_draft.id]['color'], 'gray')
        self.assertEqual(tag[self.order_draft.id]['label'], 'DRAFT')

    def test_mixin_stores_tag_on_sale_order(self):
        order = self._create_confirmed_order()
        self.assertEqual(order.rn_color_tag_color, 'green')
        self.assertEqual(order.rn_color_tag_label, 'CONFIRMED')

    def test_rule_change_recomputes_tags(self):
        self.order_draft._rn_refresh_color_tags()
        self.assertEqual(self.order_draft.rn_color_tag_color, 'gray')
        self.rule_draft.with_context(rn_skip_color_recompute=True).write({'color': 'orange', 'label': 'OPEN'})
        self.env['rn.color.rule.service'].clear_rule_cache()
        self.order_draft._rn_refresh_color_tags()
        self.assertEqual(self.order_draft.rn_color_tag_color, 'orange')
        self.assertEqual(self.order_draft.rn_color_tag_label, 'OPEN')

    def test_security_groups_exist(self):
        group = self.env.ref('rn_smart_color_tags.group_rn_color_tags_manager', raise_if_not_found=False)
        self.assertTrue(group)

    def test_web_payload_shape(self):
        order = self._create_confirmed_order()
        service = self.env['rn.color.rule.service']
        payload = service.get_tags_for_web('sale.order', [order.id])
        self.assertIn(str(order.id), payload)
        self.assertIn('css_class', payload[str(order.id)])

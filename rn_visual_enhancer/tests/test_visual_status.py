# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnVisualStatus(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].search([('sale_ok', '=', True)], limit=1)
        if not cls.product:
            cls.product = cls.env['product.product'].create({
                'name': 'Visual Enhancer Test Product',
                'type': 'consu',
                'list_price': 10.0,
                'sale_ok': True,
            })
        cls.partner = cls.env['res.partner'].create({'name': 'VISUALSTATUS Test Partner'})
        cls.order_draft = cls.env['sale.order'].with_context(rn_skip_color_refresh=True).create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1})],
        })

    def test_status_map_returns_draft_emoji(self):
        self.env['rn.color.rule'].search([('model_name', '=', 'sale.order')]).write({'active': False})
        service = self.env['rn.color.rule.service']
        service.clear_rule_cache()
        tag = service.get_tags_batch('sale.order', [self.order_draft.id])
        self.assertEqual(tag[self.order_draft.id]['emoji'], '📝')
        self.assertEqual(tag[self.order_draft.id]['label'], 'Draft')

    def test_color_rule_overrides_status_map(self):
        self.env['rn.color.rule'].with_context(rn_skip_color_recompute=True).create({
            'name': 'Override Draft',
            'model_id': self.env.ref('sale.model_sale_order').id,
            'domain': "[('partner_id.name', 'ilike', 'VISUALSTATUS%')]",
            'color': 'orange',
            'priority': 300,
            'label': 'CUSTOM',
            'emoji': '⭐',
        })
        self.env['rn.color.rule.service'].clear_rule_cache()
        self.order_draft._rn_refresh_color_tags()
        self.assertEqual(self.order_draft.rn_color_tag_label, 'CUSTOM')
        self.assertEqual(self.order_draft.rn_color_tag_emoji, '⭐')

    def test_visual_status_model_accessible(self):
        status = self.env.ref('rn_visual_enhancer.visual_status_sale_draft', raise_if_not_found=False)
        self.assertTrue(status)
        self.assertEqual(status.field_value, 'draft')

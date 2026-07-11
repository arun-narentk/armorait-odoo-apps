# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTimelineMixin(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Mixin Timeline Partner'})

    def test_sale_order_timeline_count_and_action(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        order._compute_timeline_event_count()
        self.assertGreaterEqual(order.timeline_event_count, 1)
        action = order.action_view_timeline()
        self.assertEqual(action['res_model'], 'rn.timeline.event')
        self.assertIn(('record_id', '=', order.id), action['domain'])

    def test_purchase_order_created_event(self):
        vendor = self.env['res.partner'].create({'name': 'Timeline Vendor', 'supplier_rank': 1})
        po = self.env['purchase.order'].create({'partner_id': vendor.id})
        events = self.env['rn.timeline.event'].search([
            ('model', '=', 'purchase.order'),
            ('record_id', '=', po.id),
        ])
        self.assertTrue(events.filtered(lambda event: event.name == 'RFQ Created'))

    def test_account_move_posted_template(self):
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Timeline line',
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })
        move.action_post()
        labels = self.env['rn.timeline.event'].search([
            ('model', '=', 'account.move'),
            ('record_id', '=', move.id),
        ]).mapped('name')
        self.assertIn('Draft Invoice', labels)
        self.assertIn('Invoice Posted', labels)

    def test_widget_data_rpc_shape(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        payload = order.timeline_widget_data()
        self.assertEqual(payload['record']['model'], 'sale.order')
        self.assertEqual(payload['record']['id'], order.id)
        self.assertIn('events', payload)
        self.assertIn('has_more', payload)

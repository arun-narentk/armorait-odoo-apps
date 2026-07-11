# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTimelineService(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Timeline Test Partner'})
        cls.product = cls.env['product.product'].create({
            'name': 'Timeline Test Product',
            'list_price': 100.0,
        })

    def test_create_event_and_render(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })
        service = self.env['rn.timeline.service']
        service.create_event(
            order,
            'Invoice Created',
            event_type='invoice',
            filter_category='financial',
        )
        payload = service.render_timeline(order)
        self.assertGreaterEqual(payload['total'], 2)
        names = [event['name'] for event in payload['events']]
        self.assertIn('Quotation Created', names)
        self.assertIn('Invoice Created', names)

    def test_filter_financial_events(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 50.0,
            })],
        })
        service = self.env['rn.timeline.service']
        service.create_event(order, 'Delivered', event_type='delivery', filter_category='logistics')
        service.create_event(order, 'Paid', event_type='payment', filter_category='financial')
        payload = service.render_timeline(order, filter_category='financial')
        self.assertTrue(all(event['filter_category'] == 'financial' for event in payload['events']))

    def test_state_transition_uses_template(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 75.0,
            })],
        })
        order.write({'state': 'sent'})
        labels = self.env['rn.timeline.event'].search([
            ('model', '=', 'sale.order'),
            ('record_id', '=', order.id),
        ]).mapped('name')
        self.assertIn('Quotation Sent', labels)

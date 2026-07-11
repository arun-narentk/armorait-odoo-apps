# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.rn_record_timeline.services.constants import TIMELINE_PAGE_LIMIT


@tagged('post_install', '-at_install')
class TestRnTimelineEvent(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Event Model Partner'})

    def test_search_and_count_for_record(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        Event = self.env['rn.timeline.event']
        self.assertGreaterEqual(
            Event.count_for_record('sale.order', order.id),
            1,
        )
        financial = Event.search_for_record(
            'sale.order',
            order.id,
            filter_category='financial',
        )
        self.assertTrue(all(event.filter_category == 'financial' for event in financial))

    def test_pagination_has_more(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        service = self.env['rn.timeline.service']
        for index in range(TIMELINE_PAGE_LIMIT + 3):
            service.create_event(
                order,
                f'Bulk Event {index}',
                event_type='other',
            )
        payload = service.render_timeline(order, limit=TIMELINE_PAGE_LIMIT, offset=0)
        self.assertTrue(payload['has_more'])
        self.assertEqual(len(payload['events']), TIMELINE_PAGE_LIMIT)
        page_two = service.render_timeline(
            order,
            limit=TIMELINE_PAGE_LIMIT,
            offset=TIMELINE_PAGE_LIMIT,
        )
        self.assertGreater(len(page_two['events']), 0)

    def test_open_related_document_action(self):
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Related doc line',
                'quantity': 1,
                'price_unit': 50.0,
            })],
        })
        event = self.env['rn.timeline.service'].create_event(
            move,
            'Invoice Created',
            event_type='invoice',
            related_model='account.move',
            related_res_id=move.id,
        )
        action = event.action_open_related_document()
        self.assertEqual(action['res_model'], 'account.move')
        self.assertEqual(action['res_id'], move.id)

    def test_open_related_without_link_raises(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        event = self.env['rn.timeline.event'].search([
            ('model', '=', 'sale.order'),
            ('record_id', '=', order.id),
        ], limit=1)
        with self.assertRaises(AccessError):
            event.action_open_related_document()

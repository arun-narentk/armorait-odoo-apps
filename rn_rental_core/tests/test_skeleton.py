# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnRentalCoreSkeleton(TransactionCase):
    """Phase 1 tests for ARMORA Rental Core."""

    def test_groups_exist(self):
        group = self.env.ref('rn_rental_core.group_rn_rental_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.rental.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('today_rentals', data['cards'])

    def test_availability_pricing_booking(self):
        category = self.env['rn.rental.category'].create({'name': 'Test Cat', 'code': 'TC'})
        asset = self.env['rn.rental.asset'].create({
            'name': 'Test Asset',
            'category_id': category.id,
            'daily_price': 100,
            'deposit_amount': 50,
            'state': 'available',
        })
        partner = self.env['res.partner'].create({'name': 'Rental Customer'})
        start = fields.Datetime.now()
        end = start + timedelta(days=2)
        booking = self.env['rn.rental.booking'].create({
            'partner_id': partner.id,
            'date_start': fields.Datetime.to_string(start),
            'date_end': fields.Datetime.to_string(end),
            'plan': 'daily',
            'line_ids': [(0, 0, {'asset_id': asset.id})],
        })
        self.env['rn.rental.booking.service'].reserve(booking)
        self.assertEqual(booking.state, 'reserved')
        self.assertGreater(booking.amount_total, 0)
        self.assertEqual(asset.state, 'reserved')
        available = self.env['rn.rental.availability.service'].is_available(
            asset, start, end, exclude_booking=booking
        )
        self.assertTrue(available)

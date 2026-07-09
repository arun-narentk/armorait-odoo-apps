# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHallBase(TransactionCase):
    """Phase 1 tests for ARMORA Marriage Hall Management Core."""

    def setUp(self):
        super().setUp()
        self.venue = self.env['rn.hall.venue'].create({
            'name': 'Test Venue',
            'company_id': self.env.company.id,
        })
        self.hall = self.env['rn.hall.hall'].create({
            'name': 'Test Hall',
            'venue_id': self.venue.id,
            'capacity_seated': 300,
        })

    def test_groups_exist(self):
        group = self.env.ref('rn_hall_base.group_rn_hall_counter', raise_if_not_found=False)
        self.assertTrue(group)

    def test_venue_and_hall_sequences(self):
        self.assertNotEqual(self.venue.code, 'New')
        self.assertNotEqual(self.hall.code, 'New')
        self.assertEqual(self.hall.company_id, self.env.company)

    def test_booking_workflow(self):
        start = fields.Datetime.now() + timedelta(days=30)
        end = start + timedelta(hours=10)
        booking = self.env['rn.hall.booking'].create({
            'venue_id': self.venue.id,
            'hall_id': self.hall.id,
            'function_type': 'reception',
            'date_start': start,
            'date_end': end,
            'state': 'draft',
        })
        self.assertNotEqual(booking.reference, 'New')
        booking.action_confirm()
        self.assertEqual(booking.state, 'confirmed')

    def test_conflict_detection_blocks_double_booking(self):
        start = fields.Datetime.now() + timedelta(days=40)
        end = start + timedelta(hours=8)
        self.env['rn.hall.booking'].create({
            'venue_id': self.venue.id,
            'hall_id': self.hall.id,
            'function_type': 'muhurtham',
            'date_start': start,
            'date_end': end,
            'state': 'confirmed',
        })
        with self.assertRaises(ValidationError):
            self.env['rn.hall.booking'].create({
                'venue_id': self.venue.id,
                'hall_id': self.hall.id,
                'function_type': 'reception',
                'date_start': start + timedelta(hours=2),
                'date_end': end + timedelta(hours=2),
                'state': 'confirmed',
            })

    def test_dashboard_and_upcoming_bookings(self):
        start = fields.Datetime.now() + timedelta(days=15)
        self.env['rn.hall.booking'].create({
            'venue_id': self.venue.id,
            'hall_id': self.hall.id,
            'function_type': 'engagement',
            'date_start': start,
            'date_end': start + timedelta(hours=6),
            'state': 'confirmed',
        })
        data = self.env['rn.hall.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertGreaterEqual(data['cards']['venues'], 1)
        upcoming = self.env['rn.hall.booking.service'].get_upcoming_bookings()
        self.assertTrue(upcoming)

    def test_settings_service(self):
        settings = self.env['rn.hall.venue.service'].ensure_default_settings()
        self.assertEqual(settings.company_id, self.env.company)

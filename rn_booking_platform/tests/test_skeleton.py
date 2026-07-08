# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnBookingPlatformSkeleton(TransactionCase):
    """Phase 1 tests for ARMORA Appointment Booking Pro."""

    def test_groups_exist(self):
        group = self.env.ref('rn_booking_platform.group_rn_booking_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.booking.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('today_appointments', data['cards'])

    def test_create_appointment_and_slots(self):
        industry = self.env['rn.booking.industry'].create({
            'name': 'Test Industry',
            'code': 'test_ind_%s' % self.env['rn.booking.industry'].search_count([]),
        })
        service = self.env['rn.booking.service'].create({
            'name': 'Test Service',
            'industry_id': industry.id,
            'duration_minutes': 30,
            'list_price': 25,
        })
        staff = self.env['rn.booking.staff'].create({
            'name': 'Test Staff',
            'industry_id': industry.id,
        })
        self.env['rn.booking.working.hour'].create({
            'staff_id': staff.id,
            'dayofweek': str(fields.Date.context_today(self).weekday()),
            'hour_from': 9.0,
            'hour_to': 17.0,
        })
        partner = self.env['res.partner'].create({'name': 'Booking Customer'})
        start = fields.Datetime.now() + timedelta(days=1)
        start = start.replace(hour=10, minute=0, second=0, microsecond=0)
        appt = self.env['rn.booking.booking.service'].create_appointment({
            'partner_id': partner.id,
            'service_id': service.id,
            'staff_id': staff.id,
            'start_datetime': fields.Datetime.to_string(start),
            'company_id': self.env.company.id,
        })
        self.assertTrue(appt.name)
        self.assertEqual(appt.state, 'pending')
        slots = self.env['rn.booking.availability.service'].get_slots(
            service, staff=staff, day=fields.Date.context_today(self)
        )
        self.assertIsInstance(slots, list)

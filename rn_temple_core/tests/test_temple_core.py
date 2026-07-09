# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTempleCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.devotee = cls.env['rn.temple.devotee'].create({
            'name': 'Test Devotee',
            'mobile': '9000000002',
        })
        cls.seva = cls.env.ref('rn_temple_core.seva_type_archana')

    def test_donation_record(self):
        donation_id = self.env['rn.temple.donation.service'].record_donation(
            1000, devotee_id=self.devotee.id, payment_mode='cash'
        )
        donation = self.env['rn.temple.donation'].browse(donation_id)
        self.assertEqual(donation.state, 'confirmed')
        self.assertTrue(donation.receipt_number)

    def test_seva_booking(self):
        booking_id = self.env['rn.temple.seva.service'].book_seva(
            self.devotee.id,
            self.seva.id,
            fields.Datetime.now(),
            slot_label='Morning',
        )
        booking = self.env['rn.temple.seva.booking'].browse(booking_id)
        self.assertEqual(booking.state, 'confirmed')
        self.assertTrue(booking.qr_token)

    def test_annadhanam_estimate(self):
        est = self.env['rn.temple.annadhanam.service'].estimate_ingredients(100)
        self.assertGreater(est['rice_kg'], 0)

    def test_ai_devotee_question(self):
        answer = self.env['rn.temple.insight.service'].answer_devotee_question(
            'What sevas are available tomorrow?'
        )
        self.assertTrue(answer)

    def test_receipt_search(self):
        self.env['rn.temple.donation.service'].record_donation(
            500, devotee_id=self.devotee.id, donor_name='Test Devotee'
        )
        results = self.env['rn.temple.insight.service'].search_receipts('Test Devotee')
        self.assertTrue(results)

    def test_dashboards(self):
        trustee = self.env['rn.temple.dashboard.service'].get_trustee_dashboard()
        self.assertIn('donations_month', trustee)
        office = self.env['rn.temple.dashboard.service'].get_office_dashboard()
        self.assertIn('bookings_today', office)

# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHotelCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.room_type = cls.env.ref('rn_hotel_core.room_type_standard')
        cls.room = cls.env['rn.hotel.room'].create({
            'name': '101',
            'room_type_id': cls.room_type.id,
            'floor': '1',
            'status': 'vacant',
        })
        cls.guest = cls.env['rn.hotel.guest'].create({
            'name': 'Test Guest',
            'mobile': '9000000001',
        })

    def test_reservation_and_checkin(self):
        check_in = fields.Datetime.now()
        check_out = check_in + timedelta(days=2)
        res_id = self.env['rn.hotel.reservation.service'].create_reservation(
            self.guest.id, self.room_type.id, check_in, check_out, room_id=self.room.id
        )
        folio_id = self.env['rn.hotel.front.desk.service'].check_in(res_id, room_id=self.room.id)
        self.assertTrue(folio_id)
        self.room.invalidate_recordset()
        self.assertEqual(self.room.status, 'occupied')

    def test_checkout_creates_housekeeping(self):
        check_in = fields.Datetime.now()
        check_out = check_in + timedelta(days=1)
        res = self.env['rn.hotel.reservation'].create({
            'guest_id': self.guest.id,
            'room_type_id': self.room_type.id,
            'room_id': self.room.id,
            'check_in': check_in,
            'check_out': check_out,
            'state': 'confirmed',
        })
        self.env['rn.hotel.front.desk.service'].check_in(res.id, room_id=self.room.id)
        self.env['rn.hotel.front.desk.service'].check_out(res.id)
        self.room.invalidate_recordset()
        self.assertEqual(self.room.status, 'dirty')
        self.assertTrue(self.env['rn.hotel.housekeeping.task'].search_count([('room_id', '=', self.room.id)]))

    def test_housekeeping_complete(self):
        task = self.env['rn.hotel.housekeeping.task'].create({
            'name': 'Clean 101',
            'room_id': self.room.id,
            'state': 'dirty',
        })
        self.room.status = 'dirty'
        self.env['rn.hotel.housekeeping.service'].approve_inspection(task.id)
        task.invalidate_recordset()
        self.room.invalidate_recordset()
        self.assertEqual(task.state, 'done')
        self.assertEqual(self.room.status, 'vacant')

    def test_folio_invoice(self):
        folio = self.env['rn.hotel.folio'].create({
            'guest_id': self.guest.id,
            'room_id': self.room.id,
        })
        self.env['rn.hotel.folio.service'].add_charge(
            folio.id, 'Minibar', 500.0, charge_type='minibar'
        )
        invoice_id = self.env['rn.hotel.folio.service'].generate_invoice(folio.id)
        self.assertTrue(invoice_id)

    def test_ai_pricing(self):
        data = self.env['rn.hotel.insight.service'].suggest_rate(
            self.room_type.id, fields.Datetime.now(), fields.Datetime.now()
        )
        self.assertIn('suggested_rate', data)

    def test_gm_dashboard(self):
        data = self.env['rn.hotel.dashboard.service'].get_gm_dashboard()
        self.assertIn('occupancy_pct', data)

    def test_concierge(self):
        reply = self.env['rn.hotel.insight.service'].concierge_reply('Can I get a late checkout?')
        self.assertTrue(reply)

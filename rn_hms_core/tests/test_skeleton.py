# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHmsCoreSkeleton(TransactionCase):
    """Phase 1 tests for ARMORA Hospital ERP Core."""

    def test_groups_exist(self):
        group = self.env.ref('rn_hms_core.group_rn_hms_receptionist', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.hms.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('today_appointments', data['cards'])

    def test_patient_appointment_and_bed(self):
        patient = self.env['rn.hms.patient.service'].register_patient({
            'name': 'Test Patient',
            'phone': '1111111111',
            'company_id': self.env.company.id,
        })
        self.assertTrue(patient.patient_code)
        doctor = self.env['rn.hms.doctor'].create({
            'name': 'Dr Test',
            'specialization': 'GP',
            'consulting_fee': 100,
            'consultation_minutes': 15,
        })
        start = fields.Datetime.now() + timedelta(hours=1)
        appt = self.env['rn.hms.appointment'].create({
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'start_datetime': fields.Datetime.to_string(start),
        })
        self.env['rn.hms.appointment.service'].confirm(appt)
        self.assertEqual(appt.state, 'confirmed')
        self.assertTrue(appt.token_number)
        ward = self.env['rn.hms.ward'].create({
            'name': 'Test Ward',
            'ward_type': 'general',
        })
        bed = self.env['rn.hms.bed'].create({
            'name': 'B1',
            'ward_id': ward.id,
            'state': 'available',
        })
        self.env['rn.hms.bed.service'].allocate(bed, patient)
        self.assertEqual(bed.state, 'occupied')

# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHospitalCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env['rn.hospital.patient'].create({
            'name': 'Test Patient',
            'mobile': '9999999999',
        })
        cls.doctor = cls.env['hr.employee'].create({
            'name': 'Dr Test',
            'is_doctor': True,
            'company_id': cls.env.company.id,
        })
        cls.patient.allergy_ids = [(0, 0, {'name': 'Penicillin', 'severity': 'high'})]

    def test_uhid_generated(self):
        self.assertTrue(self.patient.uhid)
        self.assertTrue(self.patient.uhid.startswith('UHID'))

    def test_book_appointment(self):
        from odoo import fields
        appt_id = self.env['rn.hospital.appointment.service'].book_appointment(
            self.patient.id,
            self.doctor.id,
            fields.Datetime.now(),
        )
        appt = self.env['rn.hospital.appointment'].browse(appt_id)
        self.assertEqual(appt.state, 'confirmed')

    def test_token_assignment(self):
        from odoo import fields
        appt = self.env['rn.hospital.appointment'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'appointment_datetime': fields.Datetime.now(),
            'state': 'confirmed',
        })
        appt.action_check_in()
        self.assertGreater(appt.token_number, 0)

    def test_emr_encounter_from_appointment(self):
        from odoo import fields
        appt = self.env['rn.hospital.appointment'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'appointment_datetime': fields.Datetime.now(),
            'state': 'waiting',
        })
        enc_id = self.env['rn.hospital.emr.service'].start_encounter_from_appointment(appt.id)
        self.assertTrue(enc_id)

    def test_prescription_allergy_warning(self):
        from odoo import fields
        enc = self.env['rn.hospital.emr.encounter'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'encounter_datetime': fields.Datetime.now(),
        })
        line_id = self.env['rn.hospital.emr.service'].add_prescription_line(
            enc.id, 'Penicillin Tablet', dosage='500mg'
        )
        line = self.env['rn.hospital.emr.prescription'].browse(line_id)
        self.assertIn('Allergy', line.ai_warning)

    def test_billing_and_invoice(self):
        line_id = self.env['rn.hospital.billing.service'].create_charge(
            self.patient.id, 'consultation', 'OPD Consultation', 500.0
        )
        self.assertTrue(line_id)
        invoice_id = self.env['rn.hospital.billing.service'].generate_invoice(self.patient.id)
        self.assertTrue(invoice_id)

    def test_ai_scribe(self):
        from odoo import fields
        enc = self.env['rn.hospital.emr.encounter'].create({
            'patient_id': self.patient.id,
            'chief_complaint': 'Fever',
            'encounter_datetime': fields.Datetime.now(),
        })
        draft = self.env['rn.hospital.insight.service'].draft_scribe(enc.id)
        self.assertIn('Fever', draft)

    def test_hospital_dashboard(self):
        data = self.env['rn.hospital.dashboard.service'].get_hospital_dashboard()
        self.assertIn('opd_today', data)

    def test_executive_ai_answer(self):
        answer = self.env['rn.hospital.insight.service'].answer_executive_question(
            'What is bed occupancy?'
        )
        self.assertTrue(answer)

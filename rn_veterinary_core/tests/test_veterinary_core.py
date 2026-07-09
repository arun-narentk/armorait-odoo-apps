# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnVeterinaryCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.owner = cls.env['rn.vet.owner'].create({
            'name': 'Test Owner',
            'mobile': '9000000004',
        })
        cls.pet = cls.env['rn.vet.pet'].create({
            'name': 'Max',
            'owner_id': cls.owner.id,
            'species': 'dog',
            'breed': 'Beagle',
        })
        cls.vet = cls.env['hr.employee'].create({'name': 'Dr Vet'})
        cls.vaccine = cls.env.ref('rn_veterinary_core.vaccine_rabies')

    def test_appointment_flow(self):
        appt_id = self.env['rn.vet.appointment.service'].schedule(
            self.pet.id, self.vet.id, fields.Datetime.now(), 'consultation'
        )
        appt = self.env['rn.vet.appointment'].browse(appt_id)
        self.assertEqual(appt.state, 'scheduled')
        self.env['rn.vet.appointment.service'].check_in(appt_id)
        self.assertEqual(appt.state, 'checked_in')

    def test_vaccination(self):
        vac_id = self.env['rn.vet.vaccination.service'].administer(
            self.pet.id, self.vaccine.id, veterinarian_id=self.vet.id
        )
        vac = self.env['rn.vet.vaccination'].browse(vac_id)
        self.assertTrue(vac.next_due_date)
        suggest = self.env['rn.vet.insight.service'].suggest_vaccines(self.pet.id)
        self.assertIn('suggested', suggest)

    def test_medical_record(self):
        rec_id = self.env['rn.vet.medical.service'].create_consultation(
            self.pet.id, 'Mild ear infection', prescription='Ear drops', veterinarian_id=self.vet.id
        )
        note = self.env['rn.vet.insight.service'].draft_clinical_note(rec_id)
        self.assertIn('Max', note)

    def test_boarding(self):
        kennel = self.env['rn.vet.kennel'].create({'name': 'K1', 'code': 'K1'})
        brd_id = self.env['rn.vet.boarding.service'].reserve(
            self.pet.id, kennel.id, fields.Datetime.now(), daily_rate=500
        )
        boarding = self.env['rn.vet.boarding'].browse(brd_id)
        boarding.action_check_in()
        self.assertEqual(boarding.state, 'checked_in')
        occ = self.env['rn.vet.boarding.service'].occupancy()
        self.assertGreaterEqual(occ['occupied'], 1)

    def test_dashboards(self):
        clinic = self.env['rn.vet.dashboard.service'].get_clinic_dashboard()
        self.assertIn('appointments_today', clinic)
        vet_dash = self.env['rn.vet.dashboard.service'].get_vet_dashboard(self.vet.id)
        self.assertIn('appointments_today', vet_dash)

    def test_business_analytics(self):
        answer = self.env['rn.vet.insight.service'].answer_business_question(
            'How many vaccinations are due?'
        )
        self.assertTrue(answer)

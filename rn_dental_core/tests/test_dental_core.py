# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnDentalCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env['rn.dental.patient'].create({
            'name': 'Test Patient',
            'mobile': '9000000003',
            'consent_signed': True,
        })
        cls.procedure = cls.env.ref('rn_dental_core.procedure_checkup')
        cls.dentist = cls.env['hr.employee'].create({'name': 'Dr Test'})

    def test_appointment_flow(self):
        start = fields.Datetime.now()
        appt_id = self.env['rn.dental.appointment.service'].schedule_appointment(
            self.patient.id, self.dentist.id, start, procedure_id=self.procedure.id
        )
        appt = self.env['rn.dental.appointment'].browse(appt_id)
        self.assertEqual(appt.state, 'scheduled')
        self.env['rn.dental.appointment.service'].check_in(appt_id)
        self.assertEqual(appt.state, 'checked_in')

    def test_tooth_charting(self):
        rec_id = self.env['rn.dental.charting.service'].set_tooth_condition(
            self.patient.id, '21', 'decay', note='Mesial decay'
        )
        chart = self.env['rn.dental.charting.service'].get_chart_summary(self.patient.id)
        self.assertEqual(chart.get('21'), 'decay')
        self.assertTrue(rec_id)

    def test_treatment_plan(self):
        plan_id = self.env['rn.dental.treatment.service'].create_plan(
            self.patient.id,
            'Test Plan',
            [{'procedure_id': self.procedure.id, 'planned_cost': 500}],
            dentist_id=self.dentist.id,
        )
        self.env['rn.dental.treatment.service'].approve_plan(plan_id)
        plan = self.env['rn.dental.treatment.plan'].browse(plan_id)
        self.assertEqual(plan.state, 'approved')

    def test_lab_workflow(self):
        lab = self.env['rn.dental.lab.request'].create({
            'patient_id': self.patient.id,
            'dentist_id': self.dentist.id,
            'work_type': 'crown',
        })
        self.env['rn.dental.lab.service'].send_to_lab(lab.id)
        self.assertEqual(lab.state, 'sent')

    def test_ai_insights(self):
        note = self.env['rn.dental.insight.service'].draft_clinical_note(
            self.patient.id, 'Mild sensitivity on cold'
        )
        self.assertIn(self.patient.name, note)
        answer = self.env['rn.dental.insight.service'].answer_revenue_question(
            'How many appointments today?'
        )
        self.assertTrue(answer)

    def test_dashboards(self):
        clinic = self.env['rn.dental.dashboard.service'].get_clinic_dashboard()
        self.assertIn('appointments_today', clinic)
        dentist = self.env['rn.dental.dashboard.service'].get_dentist_dashboard(self.dentist.id)
        self.assertIn('appointments_today', dentist)

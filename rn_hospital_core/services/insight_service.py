# -*- coding: utf-8 -*-
"""AI-ready hospital insights (heuristic Phase 1)."""

from odoo import fields, models


class RnHospitalInsightService(models.AbstractModel):
    _name = 'rn.hospital.insight.service'
    _description = 'Hospital AI Insight Service'

    def draft_scribe(self, encounter_id):
        enc = self.env['rn.hospital.emr.encounter'].browse(encounter_id)
        if not enc.exists():
            return ''
        allergies = ', '.join(enc.patient_id.allergy_ids.mapped('name')) or 'None recorded'
        return (
            f'<p><strong>Subjective:</strong> {enc.chief_complaint or "Not recorded"}</p>'
            f'<p><strong>Allergies:</strong> {allergies}</p>'
            f'<p><strong>Assessment:</strong> Draft generated for clinician review.</p>'
            f'<p><em>AI scribe draft. Doctor must verify before signing.</em></p>'
        )

    def draft_discharge(self, encounter_id):
        enc = self.env['rn.hospital.emr.encounter'].browse(encounter_id)
        if not enc.exists():
            return ''
        diagnoses = ', '.join(enc.diagnosis_ids.mapped('name')) or 'Pending'
        meds = ', '.join(enc.prescription_ids.mapped('medicine_name')) or 'None'
        return (
            f'<p><strong>Diagnosis:</strong> {diagnoses}</p>'
            f'<p><strong>Medications:</strong> {meds}</p>'
            f'<p><strong>Follow-up:</strong> Review in 7 days or earlier if symptoms worsen.</p>'
            f'<p><em>AI discharge draft. Clinician must approve before release.</em></p>'
        )

    def check_prescription_allergy(self, patient_id, medicine_name):
        patient = self.env['rn.hospital.patient'].browse(patient_id)
        med_lower = (medicine_name or '').lower()
        for allergy in patient.allergy_ids:
            if allergy.name.lower() in med_lower or med_lower in allergy.name.lower():
                return f'Allergy alert: patient allergic to {allergy.name}'
        return ''

    def answer_executive_question(self, question, company_id=None):
        company_id = company_id or self.env.company.id
        q = (question or '').lower()
        dash = self.env['rn.hospital.dashboard.service'].get_hospital_dashboard(company_id)
        if 'revenue' in q or 'income' in q:
            return f"Today's hospital charges total {dash['revenue_today']}."
        if 'occupancy' in q or 'bed' in q:
            return f"Current bed occupancy is {dash['bed_occupancy_pct']}%."
        if 'waiting' in q:
            return f"There are {dash['waiting_patients']} patients waiting in OPD queue."
        return (
            f"OPD today: {dash['opd_today']}, IP admissions: {dash['ip_admissions']}, "
            f"revenue today: {dash['revenue_today']}."
        )

# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models


class RnDentalInsightService(models.AbstractModel):
    _name = 'rn.dental.insight.service'
    _description = 'Dental AI Insight Service'

    def draft_clinical_note(self, patient_id, findings_text):
        patient = self.env['rn.dental.patient'].browse(patient_id)
        chart = self.env['rn.dental.charting.service'].get_chart_summary(patient_id)
        issues = [f'Tooth {t}: {c}' for t, c in chart.items() if c not in ('healthy', 'missing')]
        return (
            f'Patient: {patient.name}. Findings: {findings_text or "Routine exam"}. '
            f'Chart flags: {"; ".join(issues) if issues else "No major issues recorded"}.'
        )

    def suggest_recalls(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.dental.settings'].search([('company_id', '=', company_id)], limit=1)
        months = settings.recall_checkup_months if settings else 6
        cutoff = fields.Date.context_today(self) - timedelta(days=months * 30)
        patients = self.env['rn.dental.patient'].search([('company_id', '=', company_id), ('active', '=', True)])
        created = 0
        Recall = self.env['rn.dental.recall']
        for patient in patients:
            last_appt = self.env['rn.dental.appointment'].search([
                ('patient_id', '=', patient.id),
                ('state', '=', 'completed'),
            ], order='start_datetime desc', limit=1)
            if last_appt and last_appt.start_datetime.date() > cutoff:
                continue
            if Recall.search_count([
                ('patient_id', '=', patient.id),
                ('recall_type', '=', 'checkup'),
                ('state', '=', 'pending'),
            ]):
                continue
            Recall.create({
                'patient_id': patient.id,
                'recall_type': 'checkup',
                'due_date': fields.Date.context_today(self),
            })
            created += 1
        return {'recalls_created': created}

    def answer_revenue_question(self, question, company_id=None):
        q = (question or '').lower()
        company_id = company_id or self.env.company.id
        dash = self.env['rn.dental.dashboard.service'].get_clinic_dashboard(company_id)
        if 'chair' in q or 'utilization' in q:
            return f'Chair utilization today: {dash["chair_utilization"]}%.'
        if 'recall' in q or 'follow' in q:
            return f'{dash["pending_recalls"]} patients due for recall.'
        if 'appointment' in q or 'busy' in q:
            return f'{dash["appointments_today"]} appointments scheduled today.'
        if 'patient' in q or 'new' in q:
            return f'{dash["new_patients_month"]} new patients this month.'
        return (
            f'Appointments today: {dash["appointments_today"]}. '
            f'Pending recalls: {dash["pending_recalls"]}. '
            f'New patients (month): {dash["new_patients_month"]}.'
        )

    def treatment_summary_for_patient(self, plan_id):
        return self.env['rn.dental.treatment.service'].patient_summary(plan_id)

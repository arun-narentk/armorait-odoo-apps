# -*- coding: utf-8 -*-

from odoo import models


class RnDentalTreatmentService(models.AbstractModel):
    _name = 'rn.dental.treatment.service'
    _description = 'Treatment Plan Service'

    def create_plan(self, patient_id, name, line_vals_list, dentist_id=None):
        plan = self.env['rn.dental.treatment.plan'].create({
            'name': name,
            'patient_id': patient_id,
            'dentist_id': dentist_id,
            'line_ids': [(0, 0, vals) for vals in line_vals_list],
            'state': 'draft',
        })
        return plan.id

    def approve_plan(self, plan_id):
        plan = self.env['rn.dental.treatment.plan'].browse(plan_id)
        plan.write({'state': 'approved', 'consent_signed': True})
        return True

    def mark_line_done(self, line_id):
        line = self.env['rn.dental.treatment.plan.line'].browse(line_id)
        line.write({'state': 'done'})
        plan = line.plan_id
        if all(l.state == 'done' for l in plan.line_ids):
            plan.state = 'done'
        elif plan.state == 'approved':
            plan.state = 'in_progress'
        return True

    def patient_summary(self, plan_id):
        plan = self.env['rn.dental.treatment.plan'].browse(plan_id)
        lines = ', '.join(plan.line_ids.mapped('procedure_id.name'))
        return (
            f'Plan: {plan.name}. Procedures: {lines}. '
            f'Estimated cost: {plan.total_cost}. Progress: {plan.progress_pct}%.'
        )

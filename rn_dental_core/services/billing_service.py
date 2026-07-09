# -*- coding: utf-8 -*-

from odoo import models


class RnDentalBillingService(models.AbstractModel):
    _name = 'rn.dental.billing.service'
    _description = 'Dental Billing Service'

    def create_invoice_from_plan(self, plan_id, partner_id=None):
        plan = self.env['rn.dental.treatment.plan'].browse(plan_id)
        plan.ensure_one()
        partner = partner_id or plan.patient_id.partner_id or self.env.ref('base.res_partner_1', raise_if_not_found=False)
        lines = []
        for line in plan.line_ids.filtered(lambda l: l.state == 'done'):
            price = line.planned_cost or line.procedure_id.list_price
            lines.append((0, 0, {
                'name': f'{line.procedure_id.name} (Tooth {line.tooth_number or "-"})',
                'quantity': 1,
                'price_unit': price,
            }))
        if not lines:
            for line in plan.line_ids:
                lines.append((0, 0, {
                    'name': line.procedure_id.name,
                    'quantity': 1,
                    'price_unit': line.planned_cost or line.procedure_id.list_price,
                }))
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id if partner else False,
            'invoice_line_ids': lines,
        })
        return move.id

    def record_advance(self, patient_id, amount, partner_id=None):
        patient = self.env['rn.dental.patient'].browse(patient_id)
        partner = partner_id or patient.partner_id or self.env.ref('base.res_partner_1', raise_if_not_found=False)
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id if partner else False,
            'invoice_line_ids': [(0, 0, {
                'name': 'Treatment advance',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        return move.id

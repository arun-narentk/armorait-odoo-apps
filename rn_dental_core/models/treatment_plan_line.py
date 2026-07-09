# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalTreatmentPlanLine(models.Model):
    _name = 'rn.dental.treatment.plan.line'
    _description = 'Treatment Plan Line'
    _order = 'sequence, id'

    plan_id = fields.Many2one('rn.dental.treatment.plan', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    procedure_id = fields.Many2one('rn.dental.procedure', required=True)
    tooth_number = fields.Char(string='Tooth')
    visit_count = fields.Integer(default=1)
    planned_cost = fields.Float()
    state = fields.Selection(
        [('planned', 'Planned'), ('scheduled', 'Scheduled'), ('done', 'Done')],
        default='planned',
    )
    note = fields.Text()
    company_id = fields.Many2one(related='plan_id.company_id', store=True)

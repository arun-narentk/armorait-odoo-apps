# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnDentalTreatmentPlan(models.Model):
    _name = 'rn.dental.treatment.plan'
    _description = 'Dental Treatment Plan'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True)
    patient_id = fields.Many2one('rn.dental.patient', required=True, ondelete='cascade', index=True)
    dentist_id = fields.Many2one('hr.employee', string='Dentist')
    line_ids = fields.One2many('rn.dental.treatment.plan.line', 'plan_id')
    total_cost = fields.Float(compute='_compute_totals', store=True)
    progress_pct = fields.Float(string='Progress %', compute='_compute_totals', store=True)
    consent_signed = fields.Boolean()
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        default='draft',
        tracking=True,
    )
    note = fields.Html(string='Patient Summary')
    company_id = fields.Many2one(related='patient_id.company_id', store=True, index=True)

    @api.depends('line_ids.planned_cost', 'line_ids.state')
    def _compute_totals(self):
        for plan in self:
            lines = plan.line_ids
            plan.total_cost = sum(lines.mapped('planned_cost'))
            done = len(lines.filtered(lambda l: l.state == 'done'))
            plan.progress_pct = round((done / len(lines)) * 100, 1) if lines else 0.0

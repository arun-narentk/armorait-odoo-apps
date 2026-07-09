# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionMilestone(models.Model):
    _name = 'rn.construction.milestone'
    _description = 'Project Milestone'
    _order = 'target_date'

    name = fields.Char(required=True)
    construction_project_id = fields.Many2one(
        'rn.construction.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    phase_id = fields.Many2one('rn.construction.phase')
    target_date = fields.Date(required=True, index=True)
    actual_date = fields.Date()
    state = fields.Selection(
        [('pending', 'Pending'), ('done', 'Done'), ('delayed', 'Delayed')],
        default='pending',
    )
    billing_pct = fields.Float(string='Billing %')
    company_id = fields.Many2one(related='construction_project_id.company_id', store=True)

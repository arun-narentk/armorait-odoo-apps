# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionProject(models.Model):
    _name = 'rn.construction.project'
    _description = 'Construction Project'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True)
    project_id = fields.Many2one('project.project', string='Odoo Project')
    client_id = fields.Many2one('res.partner', string='Client')
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    contract_value = fields.Float()
    budget_total = fields.Float(string='Approved Budget')
    actual_cost = fields.Float(compute='_compute_costs', store=True)
    estimated_cost = fields.Float(compute='_compute_costs', store=True)
    progress_pct = fields.Float(string='Progress %', default=0.0)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('on_hold', 'On Hold'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    site_ids = fields.One2many('rn.construction.site', 'construction_project_id')
    phase_ids = fields.One2many('rn.construction.phase', 'construction_project_id')
    boq_ids = fields.One2many('rn.construction.boq', 'construction_project_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('boq_ids.estimated_total', 'boq_ids.actual_total')
    def _compute_costs(self):
        for rec in self:
            rec.estimated_cost = sum(rec.boq_ids.mapped('estimated_total'))
            rec.actual_cost = sum(rec.boq_ids.mapped('actual_total'))

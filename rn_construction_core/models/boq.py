# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionBoq(models.Model):
    _name = 'rn.construction.boq'
    _description = 'Bill of Quantities'
    _inherit = ['mail.thread']
    _order = 'version desc, id desc'

    name = fields.Char(required=True)
    construction_project_id = fields.Many2one(
        'rn.construction.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    version = fields.Integer(default=1)
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('revised', 'Revised')],
        default='draft',
        tracking=True,
    )
    line_ids = fields.One2many('rn.construction.boq.line', 'boq_id')
    estimated_total = fields.Float(compute='_compute_totals', store=True)
    actual_total = fields.Float(compute='_compute_totals', store=True)
    company_id = fields.Many2one(related='construction_project_id.company_id', store=True, index=True)

    @api.depends('line_ids.estimated_amount', 'line_ids.actual_amount')
    def _compute_totals(self):
        for boq in self:
            boq.estimated_total = sum(boq.line_ids.mapped('estimated_amount'))
            boq.actual_total = sum(boq.line_ids.mapped('actual_total'))

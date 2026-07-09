# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionCostEstimate(models.Model):
    _name = 'rn.construction.cost.estimate'
    _description = 'Cost Estimate Summary'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    construction_project_id = fields.Many2one(
        'rn.construction.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    boq_id = fields.Many2one('rn.construction.boq')
    material_cost = fields.Float()
    labour_cost = fields.Float()
    equipment_cost = fields.Float()
    subcontract_cost = fields.Float()
    overhead_cost = fields.Float()
    total_estimated = fields.Float(compute='_compute_total', store=True)
    company_id = fields.Many2one(related='construction_project_id.company_id', store=True)

    @api.depends('material_cost', 'labour_cost', 'equipment_cost', 'subcontract_cost', 'overhead_cost')
    def _compute_total(self):
        for rec in self:
            rec.total_estimated = (
                (rec.material_cost or 0) + (rec.labour_cost or 0) + (rec.equipment_cost or 0)
                + (rec.subcontract_cost or 0) + (rec.overhead_cost or 0)
            )

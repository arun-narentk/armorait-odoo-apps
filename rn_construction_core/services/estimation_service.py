# -*- coding: utf-8 -*-

from odoo import models


class RnConstructionEstimationService(models.AbstractModel):
    _name = 'rn.construction.estimation.service'
    _description = 'Cost Estimation Service'

    def build_from_boq(self, boq_id):
        boq = self.env['rn.construction.boq'].browse(boq_id)
        boq.ensure_one()
        totals = {
            'material': 0.0,
            'labour': 0.0,
            'equipment': 0.0,
            'subcontract': 0.0,
            'overhead': 0.0,
        }
        for line in boq.line_ids:
            key = line.item_type
            if key == 'subcontract':
                totals['subcontract'] += line.estimated_amount
            elif key in totals:
                totals[key] += line.estimated_amount
        estimate = self.env['rn.construction.cost.estimate'].create({
            'name': f'Estimate from {boq.name}',
            'construction_project_id': boq.construction_project_id.id,
            'boq_id': boq.id,
            'material_cost': totals['material'],
            'labour_cost': totals['labour'],
            'equipment_cost': totals['equipment'],
            'subcontract_cost': totals['subcontract'],
            'overhead_cost': totals['overhead'],
        })
        return estimate.id

    def compare_budget_vs_actual(self, project_id):
        project = self.env['rn.construction.project'].browse(project_id)
        project.ensure_one()
        variance = (project.actual_cost or 0.0) - (project.estimated_cost or 0.0)
        pct = 0.0
        if project.estimated_cost:
            pct = round((variance / project.estimated_cost) * 100, 2)
        return {
            'budget': project.budget_total or project.estimated_cost,
            'estimated': project.estimated_cost,
            'actual': project.actual_cost,
            'variance': variance,
            'variance_pct': pct,
        }

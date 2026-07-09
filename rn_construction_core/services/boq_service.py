# -*- coding: utf-8 -*-

from odoo import models


class RnConstructionBoqService(models.AbstractModel):
    _name = 'rn.construction.boq.service'
    _description = 'BOQ Service'

    def create_revision(self, boq_id):
        boq = self.env['rn.construction.boq'].browse(boq_id)
        boq.ensure_one()
        new_boq = boq.copy({
            'name': f'{boq.name} Rev {boq.version + 1}',
            'version': boq.version + 1,
            'state': 'draft',
        })
        boq.state = 'revised'
        return new_boq.id

    def approve_boq(self, boq_id):
        boq = self.env['rn.construction.boq'].browse(boq_id)
        boq.write({'state': 'approved'})
        return True

    def roll_up_from_lines(self, boq_id):
        boq = self.env['rn.construction.boq'].browse(boq_id)
        boq._compute_totals()
        return {
            'estimated_total': boq.estimated_total,
            'actual_total': boq.actual_total,
        }

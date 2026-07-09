# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetBoardingService(models.AbstractModel):
    _name = 'rn.vet.boarding.service'
    _description = 'Boarding Service'

    def reserve(self, pet_id, kennel_id, check_in, daily_rate=0.0):
        boarding = self.env['rn.vet.boarding'].create({
            'pet_id': pet_id,
            'kennel_id': kennel_id,
            'check_in': check_in,
            'daily_rate': daily_rate,
            'state': 'reserved',
        })
        return boarding.id

    def occupancy(self, company_id=None):
        company_id = company_id or self.env.company.id
        kennels = self.env['rn.vet.kennel'].search_count([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ])
        occupied = self.env['rn.vet.boarding'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'checked_in'),
        ])
        pct = round((occupied / kennels) * 100, 1) if kennels else 0.0
        return {'kennels': kennels, 'occupied': occupied, 'occupancy_pct': pct}

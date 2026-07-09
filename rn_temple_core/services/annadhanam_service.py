# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleAnnadhanamService(models.AbstractModel):
    _name = 'rn.temple.annadhanam.service'
    _description = 'Annadhanam Service'

    def plan_meal(self, meal_date, meal_type='lunch', expected_count=0, sponsor_name=None):
        meal = self.env['rn.temple.annadhanam'].create({
            'name': f'Annadhanam {meal_date} {meal_type}',
            'meal_date': meal_date,
            'meal_type': meal_type,
            'expected_count': expected_count,
            'sponsor_name': sponsor_name,
            'state': 'planned',
        })
        return meal.id

    def estimate_ingredients(self, expected_count):
        per_head_rice_kg = 0.15
        per_head_dal_kg = 0.05
        return {
            'rice_kg': round(expected_count * per_head_rice_kg, 2),
            'dal_kg': round(expected_count * per_head_dal_kg, 2),
            'note': 'Heuristic estimate based on expected meal count.',
        }

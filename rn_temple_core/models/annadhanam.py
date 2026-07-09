# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleAnnadhanam(models.Model):
    _name = 'rn.temple.annadhanam'
    _description = 'Annadhanam Record'
    _inherit = ['mail.thread']
    _order = 'meal_date desc'

    name = fields.Char(required=True)
    meal_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    meal_type = fields.Selection(
        [('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner')],
        default='lunch',
        required=True,
    )
    sponsor_devotee_id = fields.Many2one('rn.temple.devotee', string='Sponsor')
    sponsor_name = fields.Char()
    expected_count = fields.Integer(string='Expected Meals')
    actual_count = fields.Integer(string='Meals Served')
    ingredient_note = fields.Text(string='Ingredients Used')
    volunteer_ids = fields.Many2many('rn.temple.volunteer')
    cost_estimate = fields.Float()
    state = fields.Selection(
        [('planned', 'Planned'), ('served', 'Served'), ('cancelled', 'Cancelled')],
        default='planned',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

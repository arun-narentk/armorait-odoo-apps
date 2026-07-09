# -*- coding: utf-8 -*-
"""Quick bootstrap of cafe/restaurant with one branch and tables."""

from odoo import fields, models


class RnRestaurantSetupWizard(models.TransientModel):
    _name = 'rn.restaurant.setup.wizard'
    _description = 'Setup Restaurant'

    name = fields.Char(required=True, default='My Cafe')
    cuisine_type = fields.Selection(
        selection=[
            ('restaurant', 'Restaurant'),
            ('cafe', 'Cafe'),
            ('bakery', 'Bakery'),
            ('cloud_kitchen', 'Cloud Kitchen'),
            ('hotel', 'Hotel Dining'),
            ('food_truck', 'Food Truck'),
            ('other', 'Other'),
        ],
        default='cafe',
        required=True,
    )
    branch_name = fields.Char(required=True, default='Main Outlet')
    table_count = fields.Integer(default=6)
    seats_per_table = fields.Integer(default=4)
    create_defaults = fields.Boolean(string='Create Taxes & Payments', default=True)

    def action_setup(self):
        self.ensure_one()
        restaurant = self.env['rn.restaurant'].create({
            'name': self.name,
            'cuisine_type': self.cuisine_type,
        })
        branch = self.env['rn.restaurant.branch'].create({
            'name': self.branch_name,
            'restaurant_id': restaurant.id,
        })
        floor = self.env['rn.restaurant.floor'].create({
            'name': 'Main Floor',
            'branch_id': branch.id,
        })
        for idx in range(1, max(1, self.table_count) + 1):
            self.env['rn.restaurant.table'].create({
                'name': 'T%s' % idx,
                'branch_id': branch.id,
                'floor_id': floor.id,
                'seats': self.seats_per_table or 4,
            })
        if self.create_defaults:
            self.env['rn.restaurant.service'].ensure_defaults(restaurant)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.restaurant',
            'res_id': restaurant.id,
            'view_mode': 'form',
            'target': 'current',
        }

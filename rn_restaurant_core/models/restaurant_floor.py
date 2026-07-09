# -*- coding: utf-8 -*-
"""Dining area / floor plan container."""

from odoo import fields, models


class RnRestaurantFloor(models.Model):
    """Dining area such as indoor, terrace, or private room."""

    _name = 'rn.restaurant.floor'
    _description = 'Restaurant Dining Area'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    branch_id = fields.Many2one('rn.restaurant.branch', required=True, ondelete='cascade', index=True)
    restaurant_id = fields.Many2one(
        related='branch_id.restaurant_id',
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        related='branch_id.company_id',
        store=True,
        index=True,
    )
    table_ids = fields.One2many('rn.restaurant.table', 'floor_id', string='Tables')
    color = fields.Integer(string='Color Index')
    note = fields.Char()

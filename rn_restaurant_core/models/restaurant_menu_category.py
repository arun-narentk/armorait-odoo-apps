# -*- coding: utf-8 -*-
"""Menu category taxonomy."""

from odoo import fields, models


class RnRestaurantMenuCategory(models.Model):
    """Menu section such as Starters, Beverages, Desserts."""

    _name = 'rn.restaurant.menu.category'
    _description = 'Restaurant Menu Category'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    restaurant_id = fields.Many2one('rn.restaurant', required=True, ondelete='cascade', index=True)
    parent_id = fields.Many2one('rn.restaurant.menu.category', string='Parent', ondelete='set null')
    company_id = fields.Many2one(
        related='restaurant_id.company_id',
        store=True,
        index=True,
    )
    item_ids = fields.One2many('rn.restaurant.menu.item', 'category_id', string='Items')
    color = fields.Integer()
    note = fields.Char()

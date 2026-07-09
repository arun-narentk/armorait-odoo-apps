# -*- coding: utf-8 -*-
"""Dining table with POS / QR readiness."""

from odoo import api, fields, models


class RnRestaurantTable(models.Model):
    """Table used by POS, KDS, and QR ordering modules."""

    _name = 'rn.restaurant.table'
    _description = 'Restaurant Table'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True, copy=False, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    branch_id = fields.Many2one('rn.restaurant.branch', required=True, ondelete='cascade', index=True)
    floor_id = fields.Many2one('rn.restaurant.floor', ondelete='set null', index=True)
    restaurant_id = fields.Many2one(
        related='branch_id.restaurant_id',
        store=True,
        index=True,
    )
    seats = fields.Integer(default=4)
    shape = fields.Selection(
        selection=[
            ('square', 'Square'),
            ('round', 'Round'),
            ('rect', 'Rectangle'),
            ('bar', 'Bar'),
        ],
        default='square',
    )
    state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('occupied', 'Occupied'),
            ('reserved', 'Reserved'),
            ('dirty', 'Needs Cleaning'),
            ('blocked', 'Blocked'),
        ],
        default='available',
        required=True,
        tracking=True,
        index=True,
    )
    qr_token = fields.Char(copy=False, index=True, help='Reserved for rn_restaurant_qr.')
    pos_ready = fields.Boolean(default=True, string='POS Enabled')
    company_id = fields.Many2one(
        related='branch_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.restaurant.table') or 'New'
        return super().create(vals_list)

    def action_set_available(self):
        self.write({'state': 'available'})
        return True

    def action_set_occupied(self):
        self.write({'state': 'occupied'})
        return True

    def action_set_dirty(self):
        self.write({'state': 'dirty'})
        return True

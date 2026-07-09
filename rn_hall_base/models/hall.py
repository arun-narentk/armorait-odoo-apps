# -*- coding: utf-8 -*-
"""Rentable halls within a venue."""

from odoo import api, fields, models


class RnHallHall(models.Model):
    """Individual marriage hall, banquet room, or event space."""

    _name = 'rn.hall.hall'
    _description = 'Event Hall'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    venue_id = fields.Many2one(
        'rn.hall.venue',
        required=True,
        ondelete='cascade',
        index=True,
    )
    capacity_seated = fields.Integer(string='Seated Capacity', default=200)
    capacity_standing = fields.Integer(string='Standing Capacity')
    area_sqft = fields.Float(string='Area (sq ft)')
    floor_level = fields.Char()
    has_ac = fields.Boolean(string='Air Conditioned', default=True)
    has_parking = fields.Boolean(string='Parking Available', default=True)
    parking_slots = fields.Integer()
    has_dining_hall = fields.Boolean(string='Dining Hall')
    has_kitchen = fields.Boolean(string='Kitchen')
    has_stage = fields.Boolean(string='Stage', default=True)
    booking_ids = fields.One2many('rn.hall.booking', 'hall_id', string='Bookings')
    booking_count = fields.Integer(compute='_compute_booking_count')
    company_id = fields.Many2one(
        related='venue_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for hall in self:
            hall.booking_count = len(hall.booking_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.hall.hall') or 'New'
        return super().create(vals_list)

    def action_open_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bookings',
            'res_model': 'rn.hall.booking',
            'view_mode': 'calendar,list,form',
            'domain': [('hall_id', '=', self.id)],
            'context': {'default_hall_id': self.id, 'default_venue_id': self.venue_id.id},
        }

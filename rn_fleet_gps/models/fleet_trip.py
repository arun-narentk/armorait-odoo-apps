# -*- coding: utf-8 -*-
"""Trip aggregation between start and end locations."""

from odoo import api, fields, models


class RnFleetTrip(models.Model):
    """Completed or running vehicle trip."""

    _name = 'rn.fleet.trip'
    _description = 'Fleet Trip'
    _inherit = ['mail.thread']
    _order = 'date_start desc, id desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, index=True, tracking=True)
    driver_id = fields.Many2one('res.partner', string='Driver', index=True)
    device_id = fields.Many2one('rn.fleet.gps.device', index=True)
    date_start = fields.Datetime(required=True, index=True)
    date_end = fields.Datetime(index=True)
    start_latitude = fields.Float(digits=(10, 7))
    start_longitude = fields.Float(digits=(10, 7))
    end_latitude = fields.Float(digits=(10, 7))
    end_longitude = fields.Float(digits=(10, 7))
    destination = fields.Char()
    distance_km = fields.Float(string='Distance (km)')
    duration_minutes = fields.Float(compute='_compute_duration', store=True)
    idle_minutes = fields.Float()
    avg_speed = fields.Float(string='Average Speed')
    max_speed = fields.Float(string='Maximum Speed')
    fuel_used = fields.Float(string='Fuel Used (L)')
    state = fields.Selection(
        selection=[
            ('running', 'Running'),
            ('done', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='running',
        tracking=True,
        index=True,
    )
    expense_total = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for trip in self:
            if trip.date_start and trip.date_end:
                trip.duration_minutes = (trip.date_end - trip.date_start).total_seconds() / 60.0
            else:
                trip.duration_minutes = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.fleet.trip') or 'New'
        return super().create(vals_list)

    def action_close(self):
        return self.env['rn.fleet.trip.service'].close_trips(self)

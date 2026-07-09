# -*- coding: utf-8 -*-
"""Fuel fill and efficiency logs."""

from odoo import api, fields, models


class RnFleetFuelLog(models.Model):
    """Manual or sensor-based fuel event."""

    _name = 'rn.fleet.fuel.log'
    _description = 'Fleet Fuel Log'
    _order = 'date desc, id desc'

    name = fields.Char(required=True, default='Fuel Log')
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, index=True)
    driver_id = fields.Many2one('res.partner', string='Driver')
    date = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    liters = fields.Float(required=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    odometer = fields.Float()
    event_type = fields.Selection(
        selection=[
            ('fill', 'Fuel Fill'),
            ('theft', 'Fuel Theft'),
            ('sensor', 'Sensor Reading'),
        ],
        default='fill',
        required=True,
    )
    efficiency = fields.Float(
        string='Km / L',
        compute='_compute_efficiency',
        store=True,
    )
    previous_odometer = fields.Float()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.depends('odometer', 'previous_odometer', 'liters')
    def _compute_efficiency(self):
        for log in self:
            dist = (log.odometer or 0.0) - (log.previous_odometer or 0.0)
            if dist > 0 and log.liters:
                log.efficiency = dist / log.liters
            else:
                log.efficiency = 0.0

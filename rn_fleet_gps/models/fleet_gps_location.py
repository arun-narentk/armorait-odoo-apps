# -*- coding: utf-8 -*-
"""GPS location points."""

from odoo import api, fields, models


class RnFleetGpsLocation(models.Model):
    """Single telemetry point for a vehicle / device."""

    _name = 'rn.fleet.gps.location'
    _description = 'Fleet GPS Location'
    _order = 'timestamp desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    device_id = fields.Many2one('rn.fleet.gps.device', required=True, ondelete='cascade', index=True)
    vehicle_id = fields.Many2one('fleet.vehicle', index=True)
    timestamp = fields.Datetime(required=True, index=True, default=fields.Datetime.now)
    latitude = fields.Float(digits=(10, 7), required=True)
    longitude = fields.Float(digits=(10, 7), required=True)
    speed = fields.Float(string='Speed (km/h)')
    heading = fields.Float(string='Direction')
    altitude = fields.Float()
    accuracy = fields.Float(string='GPS Accuracy (m)')
    ignition = fields.Boolean()
    engine_on = fields.Boolean(string='Engine Status')
    odometer = fields.Float(string='Odometer (km)')
    raw_payload = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('vehicle_id', 'device_id', 'timestamp')
    def _compute_name(self):
        for rec in self:
            vehicle = rec.vehicle_id.name or (rec.device_id.name if rec.device_id else 'GPS')
            rec.name = '%s @ %s' % (vehicle, rec.timestamp or '')

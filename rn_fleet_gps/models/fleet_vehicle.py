# -*- coding: utf-8 -*-
"""Extend fleet.vehicle with GPS summary fields."""

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    rn_gps_device_ids = fields.One2many('rn.fleet.gps.device', 'vehicle_id', string='GPS Devices')
    rn_gps_device_id = fields.Many2one(
        'rn.fleet.gps.device',
        string='Primary GPS Device',
        compute='_compute_rn_gps_device',
        store=True,
    )
    rn_last_latitude = fields.Float(digits=(10, 7), string='Last Latitude')
    rn_last_longitude = fields.Float(digits=(10, 7), string='Last Longitude')
    rn_last_speed = fields.Float(string='Last Speed')
    rn_last_gps_at = fields.Datetime(string='Last GPS Signal')
    rn_gps_online = fields.Boolean(string='GPS Online')
    rn_trip_ids = fields.One2many('rn.fleet.trip', 'vehicle_id', string='Trips')
    rn_alert_ids = fields.One2many('rn.fleet.alert', 'vehicle_id', string='GPS Alerts')

    @api.depends('rn_gps_device_ids')
    def _compute_rn_gps_device(self):
        for vehicle in self:
            vehicle.rn_gps_device_id = vehicle.rn_gps_device_ids[:1]

    def action_open_rn_live_map(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_fleet_gps.dashboard',
            'name': 'Fleet Live Map',
            'params': {'vehicle_id': self.id},
        }

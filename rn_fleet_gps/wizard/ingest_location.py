# -*- coding: utf-8 -*-
"""Manual GPS point ingest for demos and testing."""

from odoo import fields, models


class RnFleetIngestLocationWizard(models.TransientModel):
    _name = 'rn.fleet.ingest.location.wizard'
    _description = 'Ingest GPS Location'

    device_id = fields.Many2one('rn.fleet.gps.device', required=True)
    latitude = fields.Float(digits=(10, 7), required=True)
    longitude = fields.Float(digits=(10, 7), required=True)
    speed = fields.Float()
    ignition = fields.Boolean()
    odometer = fields.Float()

    def action_ingest(self):
        self.ensure_one()
        location = self.env['rn.fleet.location.service'].ingest(self.device_id, {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'ignition': self.ignition,
            'engine_on': self.ignition,
            'odometer': self.odometer,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.fleet.gps.location',
            'res_id': location.id,
            'view_mode': 'form',
            'target': 'current',
        }

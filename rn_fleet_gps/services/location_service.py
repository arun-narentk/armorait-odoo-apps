# -*- coding: utf-8 -*-
"""Location ingest and vehicle state update."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnFleetLocationService(models.AbstractModel):
    _name = 'rn.fleet.location.service'
    _description = 'Fleet Location Service'

    def ingest(self, device, vals):
        """Create location, refresh vehicle GPS fields, run trip/geofence/alerts."""
        device.ensure_one()
        if not vals.get('latitude') or not vals.get('longitude'):
            return self.env['rn.fleet.gps.location']
        timestamp = vals.get('timestamp') or fields.Datetime.now()
        if isinstance(timestamp, str):
            timestamp = fields.Datetime.to_datetime(timestamp)
        location = self.env['rn.fleet.gps.location'].create({
            'device_id': device.id,
            'vehicle_id': device.vehicle_id.id if device.vehicle_id else False,
            'timestamp': timestamp,
            'latitude': float(vals['latitude']),
            'longitude': float(vals['longitude']),
            'speed': float(vals.get('speed') or 0.0),
            'heading': float(vals.get('heading') or 0.0),
            'altitude': float(vals.get('altitude') or 0.0),
            'accuracy': float(vals.get('accuracy') or 0.0),
            'ignition': bool(vals.get('ignition')),
            'engine_on': bool(vals.get('engine_on')),
            'odometer': float(vals.get('odometer') or 0.0),
            'raw_payload': vals.get('raw_payload'),
            'company_id': device.company_id.id,
        })
        device.last_location_id = location.id
        if device.vehicle_id:
            device.vehicle_id.write({
                'rn_last_latitude': location.latitude,
                'rn_last_longitude': location.longitude,
                'rn_last_speed': location.speed,
                'rn_last_gps_at': location.timestamp,
                'rn_gps_online': True,
            })
            self.env['rn.fleet.trip.service'].on_location(device.vehicle_id, location)
            self.env['rn.fleet.geofence.service'].evaluate(device.vehicle_id, location)
            self.env['rn.fleet.alert.service'].evaluate_location(device.vehicle_id, location, device)
        _logger.info('Ingested GPS location %s for device %s', location.id, device.code)
        return location

# -*- coding: utf-8 -*-
"""Device trust and geo validation helpers."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrDeviceService(models.AbstractModel):
    """Register and validate kiosk devices and geo fence."""

    _name = 'rn.hr.device.service'
    _description = 'Face Attendance Device Service'

    def register_or_update(self, fingerprint):
        """Create or update a recognition device from browser fingerprint."""
        Device = self.env['rn.hr.recognition.device']
        serial = fingerprint.get('serial_number') or fingerprint.get('user_agent', '')[:64]
        device = Device.search([('serial_number', '=', serial)], limit=1)
        vals = {
            'name': fingerprint.get('name') or serial or 'Kiosk Device',
            'serial_number': serial,
            'browser': fingerprint.get('browser'),
            'operating_system': fingerprint.get('operating_system'),
            'user_agent': fingerprint.get('user_agent'),
            'last_seen': fields.Datetime.now(),
        }
        if device:
            device.write(vals)
            return device
        vals['state'] = 'pending'
        return Device.create(vals)

    def is_allowed(self, device):
        """Return True when device may punch attendance."""
        device.ensure_one()
        return device.state in ('allowed', 'trusted')

    def validate_geo(self, camera, latitude, longitude):
        """Check attendance coordinates against camera branch radius."""
        camera.ensure_one()
        # Phase 7: haversine distance vs allowed_radius_m.
        _logger.debug('geo validate camera=%s lat=%s lng=%s', camera.id, latitude, longitude)
        return {'ok': True, 'within_radius': True, 'distance_m': 0.0}

# -*- coding: utf-8 -*-
"""Traccar connector stub for dedicated add-on / Phase later."""

import json
import logging
import urllib.error
import urllib.request

from odoo import models

_logger = logging.getLogger(__name__)


class RnFleetGpsProviderTraccar(models.AbstractModel):
    _name = 'rn.fleet.gps.provider.traccar'
    _inherit = 'rn.fleet.gps.provider.base'
    _description = 'Fleet GPS Traccar Provider'

    def test_connection(self, device):
        if not device.api_url:
            return {'ok': False, 'message': 'Set Provider API URL (Traccar server)'}
        return {'ok': True, 'message': 'Traccar adapter ready (live poll in connector polish)'}

    def fetch_latest(self, device):
        if not device.api_url or not device.device_uid:
            return False
        # Soft poll stub: companion rn_fleet_gps_traccar can replace HTTP details
        url = device.api_url.rstrip('/') + '/api/positions'
        try:
            req = urllib.request.Request(
                url,
                headers={'Authorization': 'Bearer %s' % (device.api_token or '')},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, list) and data:
                pos = data[0]
                return {
                    'latitude': pos.get('latitude'),
                    'longitude': pos.get('longitude'),
                    'speed': pos.get('speed'),
                    'heading': pos.get('course'),
                    'timestamp': pos.get('deviceTime') or pos.get('fixTime'),
                    'raw_payload': json.dumps(pos),
                }
        except Exception as exc:  # noqa: BLE001
            _logger.info('Traccar fetch skipped/failed: %s', exc)
        return False

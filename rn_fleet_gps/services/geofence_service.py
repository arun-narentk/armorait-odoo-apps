# -*- coding: utf-8 -*-
"""Geofence enter/exit evaluation."""

import logging
import math

from odoo import models

_logger = logging.getLogger(__name__)


class RnFleetGeofenceService(models.AbstractModel):
    _name = 'rn.fleet.geofence.service'
    _description = 'Fleet Geofence Service'

    def _distance_m(self, lat1, lon1, lat2, lon2):
        r = 6371000.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlmb = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
        return 2 * r * math.asin(min(1.0, math.sqrt(a)))

    def evaluate(self, vehicle, location):
        settings = self.env['rn.fleet.settings'].search(
            [('company_id', '=', vehicle.company_id.id)], limit=1
        )
        if settings and not settings.enable_geofence_alerts:
            return True
        fences = self.env['rn.fleet.geofence'].search([
            ('active', '=', True),
            ('company_id', '=', vehicle.company_id.id),
        ])
        for fence in fences:
            dist = self._distance_m(location.latitude, location.longitude, fence.latitude, fence.longitude)
            inside = dist <= (fence.radius_m or 0.0)
            # Phase 1 raises enter when currently inside (idempotent enough for demo)
            if inside and fence.alert_on_enter:
                existing = self.env['rn.fleet.alert'].search([
                    ('vehicle_id', '=', vehicle.id),
                    ('geofence_id', '=', fence.id),
                    ('alert_type', '=', 'geofence_enter'),
                    ('state', '=', 'open'),
                ], limit=1)
                if not existing:
                    self.env['rn.fleet.alert.service'].raise_alert(
                        'geofence_enter',
                        'Entered %s' % fence.name,
                        vehicle=vehicle,
                        geofence=fence,
                        severity='info',
                    )
        return True

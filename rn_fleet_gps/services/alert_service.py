# -*- coding: utf-8 -*-
"""Alert evaluation helpers."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnFleetAlertService(models.AbstractModel):
    _name = 'rn.fleet.alert.service'
    _description = 'Fleet Alert Service'

    def raise_alert(self, alert_type, name, vehicle=None, device=None, geofence=None, severity='warning', value=0.0, threshold=0.0):
        company = self.env.company
        if vehicle:
            company = vehicle.company_id
        elif device:
            company = device.company_id
        return self.env['rn.fleet.alert'].create({
            'name': name,
            'alert_type': alert_type,
            'severity': severity,
            'vehicle_id': vehicle.id if vehicle else False,
            'device_id': device.id if device else False,
            'geofence_id': geofence.id if geofence else False,
            'value': value,
            'threshold': threshold,
            'company_id': company.id,
        })

    def evaluate_location(self, vehicle, location, device=None):
        settings = self.env['rn.fleet.settings'].search(
            [('company_id', '=', vehicle.company_id.id)], limit=1
        )
        limit = settings.overspeed_limit if settings else (vehicle.company_id.rn_fleet_overspeed_limit or 80.0)
        if location.speed and location.speed > limit:
            self.raise_alert(
                'overspeed',
                'Overspeed %s km/h on %s' % (location.speed, vehicle.name),
                vehicle=vehicle,
                device=device,
                severity='warning',
                value=location.speed,
                threshold=limit,
            )
        return True

    def cron_offline_alerts(self):
        now = fields.Datetime.now()
        for settings in self.env['rn.fleet.settings'].search([]):
            minutes = settings.offline_minutes or 10
            devices = self.env['rn.fleet.gps.device'].search([
                ('company_id', '=', settings.company_id.id),
                ('state', '=', 'active'),
                ('vehicle_id', '!=', False),
            ])
            for device in devices:
                if not device.last_seen:
                    continue
                delta = (now - device.last_seen).total_seconds() / 60.0
                if delta >= minutes and device.vehicle_id:
                    device.vehicle_id.rn_gps_online = False
                    open_alert = self.env['rn.fleet.alert'].search([
                        ('vehicle_id', '=', device.vehicle_id.id),
                        ('alert_type', '=', 'offline'),
                        ('state', '=', 'open'),
                    ], limit=1)
                    if not open_alert:
                        self.raise_alert(
                            'offline',
                            'Vehicle offline: %s' % device.vehicle_id.name,
                            vehicle=device.vehicle_id,
                            device=device,
                            severity='critical',
                        )
        return True

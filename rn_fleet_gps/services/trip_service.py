# -*- coding: utf-8 -*-
"""Trip start/stop engine from movement."""

import logging
import math
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnFleetTripService(models.AbstractModel):
    _name = 'rn.fleet.trip.service'
    _description = 'Fleet Trip Service'

    def on_location(self, vehicle, location):
        Trip = self.env['rn.fleet.trip']
        running = Trip.search([
            ('vehicle_id', '=', vehicle.id),
            ('state', '=', 'running'),
        ], limit=1)
        moving = (location.speed or 0.0) >= 3.0 or location.ignition or location.engine_on
        if moving and not running:
            Trip.create({
                'vehicle_id': vehicle.id,
                'driver_id': vehicle.driver_id.id if vehicle.driver_id else False,
                'device_id': location.device_id.id,
                'date_start': location.timestamp,
                'start_latitude': location.latitude,
                'start_longitude': location.longitude,
                'max_speed': location.speed or 0.0,
                'company_id': vehicle.company_id.id,
            })
            return True
        if running:
            vals = {
                'max_speed': max(running.max_speed or 0.0, location.speed or 0.0),
            }
            if location.odometer and running.start_latitude:
                # rough distance accumulate using haversine from start if blank midpoints
                pass
            # update end preview while running
            vals.update({
                'end_latitude': location.latitude,
                'end_longitude': location.longitude,
            })
            if (location.speed or 0.0) > 0 and running.date_start:
                # naive avg
                minutes = max((location.timestamp - running.date_start).total_seconds() / 60.0, 1.0)
                dist = self._haversine(
                    running.start_latitude, running.start_longitude,
                    location.latitude, location.longitude,
                )
                vals['distance_km'] = dist
                vals['avg_speed'] = (dist / minutes) * 60.0 if minutes else 0.0
            running.write(vals)
            settings = self.env['rn.fleet.settings'].search(
                [('company_id', '=', vehicle.company_id.id)], limit=1
            )
            idle_limit = settings.auto_close_trip_idle_minutes if settings else 20
            if not moving and location.timestamp and running.date_start:
                # close if last movement older than threshold handled by scheduler preferring
                pass
        return True

    def close_trips(self, trips):
        for trip in trips.filtered(lambda t: t.state == 'running'):
            end = fields.Datetime.now()
            dist = trip.distance_km
            if trip.start_latitude and trip.end_latitude:
                dist = self._haversine(
                    trip.start_latitude, trip.start_longitude,
                    trip.end_latitude, trip.end_longitude,
                )
            trip.write({
                'state': 'done',
                'date_end': trip.date_end or end,
                'distance_km': dist,
            })
        return True

    def cron_auto_close(self):
        settings_map = {
            s.company_id.id: s.auto_close_trip_idle_minutes or 20
            for s in self.env['rn.fleet.settings'].search([])
        }
        running = self.env['rn.fleet.trip'].search([('state', '=', 'running')])
        now = fields.Datetime.now()
        for trip in running:
            limit = settings_map.get(trip.company_id.id, 20)
            last = trip.vehicle_id.rn_last_gps_at
            if last and (now - last) >= timedelta(minutes=limit):
                if trip.vehicle_id.rn_last_latitude:
                    trip.end_latitude = trip.vehicle_id.rn_last_latitude
                    trip.end_longitude = trip.vehicle_id.rn_last_longitude
                self.close_trips(trip)
        return True

    def _haversine(self, lat1, lon1, lat2, lon2):
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0
        r = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlmb = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
        return 2 * r * math.asin(min(1.0, math.sqrt(a)))

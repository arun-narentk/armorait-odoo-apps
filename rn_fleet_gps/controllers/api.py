# -*- coding: utf-8 -*-
"""Public health + authenticated REST-style JSON endpoints."""

import json

from odoo import http
from odoo.http import request


class RnFleetApiController(http.Controller):

    @http.route('/rn_fleet_gps/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'ok': True, 'module': 'rn_fleet_gps'})

    @http.route('/api/rn_fleet/v1/dashboard', type='json', auth='user')
    def api_dashboard(self):
        return {'ok': True, 'data': request.env['rn.fleet.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_fleet/v1/vehicles', type='json', auth='user')
    def api_vehicles(self):
        vehicles = request.env['fleet.vehicle'].search([('company_id', '=', request.env.company.id)])
        return {'ok': True, 'data': [{
            'id': v.id,
            'name': v.name,
            'lat': v.rn_last_latitude,
            'lng': v.rn_last_longitude,
            'speed': v.rn_last_speed,
            'online': v.rn_gps_online,
        } for v in vehicles]}

    @http.route('/api/rn_fleet/v1/location', type='json', auth='user')
    def api_location_push(self, device_code=None, device_id=None, **vals):
        Device = request.env['rn.fleet.gps.device']
        device = Device.browse(device_id) if device_id else Device.search([('code', '=', device_code)], limit=1)
        if not device:
            return {'ok': False, 'error': 'Device not found'}
        location = request.env['rn.fleet.location.service'].ingest(device, vals)
        return {'ok': True, 'location_id': location.id if location else False}

    @http.route('/api/rn_fleet/v1/trips', type='json', auth='user')
    def api_trips(self, limit=50):
        trips = request.env['rn.fleet.trip'].search([], limit=int(limit or 50))
        return {'ok': True, 'data': [{
            'id': t.id,
            'name': t.name,
            'vehicle': t.vehicle_id.name,
            'distance_km': t.distance_km,
            'state': t.state,
        } for t in trips]}

    @http.route('/api/rn_fleet/v1/alerts', type='json', auth='user')
    def api_alerts(self):
        alerts = request.env['rn.fleet.alert'].search([('state', '=', 'open')], limit=50)
        return {'ok': True, 'data': [{'id': a.id, 'name': a.name, 'type': a.alert_type} for a in alerts]}

    @http.route('/api/rn_fleet/v1/drivers', type='json', auth='user')
    def api_drivers(self):
        assigns = request.env['rn.fleet.driver.assignment'].search([('state', '=', 'open')])
        return {'ok': True, 'data': [{
            'id': a.id,
            'driver': a.driver_id.name,
            'vehicle': a.vehicle_id.name,
        } for a in assigns]}

    @http.route('/api/rn_fleet/v1/fuel', type='json', auth='user')
    def api_fuel(self, limit=50):
        logs = request.env['rn.fleet.fuel.log'].search([], limit=int(limit or 50))
        return {'ok': True, 'data': [{
            'id': l.id,
            'vehicle': l.vehicle_id.name,
            'liters': l.liters,
            'amount': l.amount,
        } for l in logs]}

# -*- coding: utf-8 -*-
"""Fleet GPS KPI payload."""

from datetime import timedelta

from odoo import fields, models


class RnFleetDashboardService(models.AbstractModel):
    _name = 'rn.fleet.dashboard.service'
    _description = 'Fleet Dashboard Service'

    def get_dashboard_data(self, company_id=None, vehicle_id=None):
        company_id = company_id or self.env.company.id
        Vehicle = self.env['fleet.vehicle']
        Trip = self.env['rn.fleet.trip']
        Alert = self.env['rn.fleet.alert']
        domain_v = [('company_id', '=', company_id)]
        if vehicle_id:
            domain_v.append(('id', '=', vehicle_id))
        vehicles = Vehicle.search(domain_v)
        today = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        cards = {
            'active_vehicles': len(vehicles),
            'moving': len(vehicles.filtered(lambda v: v.rn_gps_online and (v.rn_last_speed or 0) >= 3)),
            'idle': len(vehicles.filtered(lambda v: v.rn_gps_online and (v.rn_last_speed or 0) < 3)),
            'offline': len(vehicles.filtered(lambda v: not v.rn_gps_online)),
            'trips_today': Trip.search_count([
                ('company_id', '=', company_id),
                ('date_start', '>=', today),
            ]),
            'open_alerts': Alert.search_count([
                ('company_id', '=', company_id),
                ('state', '=', 'open'),
            ]),
            'distance_today': sum(Trip.search([
                ('company_id', '=', company_id),
                ('date_start', '>=', today),
            ]).mapped('distance_km')),
            'fuel_cost_month': sum(self.env['rn.fleet.fuel.log'].search([
                ('company_id', '=', company_id),
                ('date', '>=', fields.Datetime.now() - timedelta(days=30)),
            ]).mapped('amount')),
        }
        map_points = [{
            'id': v.id,
            'name': v.name,
            'lat': v.rn_last_latitude,
            'lng': v.rn_last_longitude,
            'speed': v.rn_last_speed,
            'online': v.rn_gps_online,
        } for v in vehicles if v.rn_last_latitude and v.rn_last_longitude]
        sub = self.env['rn.fleet.subscription'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ['trial', 'active']),
        ], limit=1)
        return {
            'cards': cards,
            'map_points': map_points,
            'edition': sub.plan if sub else 'base',
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

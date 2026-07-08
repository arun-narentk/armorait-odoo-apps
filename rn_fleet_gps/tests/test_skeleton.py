# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnFleetGps(TransactionCase):

    def test_groups_exist(self):
        group = self.env.ref('rn_fleet_gps.group_rn_fleet_gps_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.fleet.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('map_points', data)

    def test_ingest_location_and_trip(self):
        brand = self.env['fleet.vehicle.model.brand'].create({'name': 'ARMORA Test Brand'})
        model = self.env['fleet.vehicle.model'].create({
            'name': 'Test Model',
            'brand_id': brand.id,
        })
        vehicle = self.env['fleet.vehicle'].create({
            'model_id': model.id,
            'license_plate': 'TST-GPS-1',
        })
        device = self.env['rn.fleet.gps.device'].create({
            'name': 'Tracker A',
            'provider': 'manual',
            'vehicle_id': vehicle.id,
            'state': 'active',
        })
        loc1 = self.env['rn.fleet.location.service'].ingest(device, {
            'latitude': 11.0,
            'longitude': 76.9,
            'speed': 40.0,
            'ignition': True,
        })
        self.assertTrue(loc1)
        self.assertTrue(vehicle.rn_gps_online)
        self.assertGreater(vehicle.rn_last_speed, 0)
        trip = self.env['rn.fleet.trip'].search([('vehicle_id', '=', vehicle.id), ('state', '=', 'running')], limit=1)
        self.assertTrue(trip)
        # overspeed alert
        self.env['rn.fleet.location.service'].ingest(device, {
            'latitude': 11.01,
            'longitude': 76.91,
            'speed': 120.0,
            'ignition': True,
        })
        alert = self.env['rn.fleet.alert'].search([
            ('vehicle_id', '=', vehicle.id),
            ('alert_type', '=', 'overspeed'),
        ], limit=1)
        self.assertTrue(alert)

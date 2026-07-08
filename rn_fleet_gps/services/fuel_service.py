# -*- coding: utf-8 -*-
"""Fuel logging helpers."""

from odoo import models


class RnFleetFuelService(models.AbstractModel):
    _name = 'rn.fleet.fuel.service'
    _description = 'Fleet Fuel Service'

    def register_fill(self, vehicle, liters, amount=0.0, odometer=0.0, driver=None):
        previous = self.env['rn.fleet.fuel.log'].search([
            ('vehicle_id', '=', vehicle.id),
            ('event_type', '=', 'fill'),
        ], order='date desc, id desc', limit=1)
        return self.env['rn.fleet.fuel.log'].create({
            'name': 'Fuel fill %s' % (vehicle.name or ''),
            'vehicle_id': vehicle.id,
            'driver_id': driver.id if driver else False,
            'liters': liters,
            'amount': amount,
            'odometer': odometer,
            'previous_odometer': previous.odometer if previous else 0.0,
            'event_type': 'fill',
            'company_id': vehicle.company_id.id,
        })

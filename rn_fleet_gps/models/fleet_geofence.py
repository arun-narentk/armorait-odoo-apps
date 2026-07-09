# -*- coding: utf-8 -*-
"""Circular geofence zones."""

from odoo import fields, models


class RnFleetGeofence(models.Model):
    """Named zone for enter / exit alerts."""

    _name = 'rn.fleet.geofence'
    _description = 'Fleet Geofence'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    zone_type = fields.Selection(
        selection=[
            ('warehouse', 'Warehouse'),
            ('customer', 'Customer Site'),
            ('factory', 'Factory'),
            ('office', 'Office'),
            ('restricted', 'Restricted Area'),
            ('other', 'Other'),
        ],
        default='warehouse',
        required=True,
    )
    latitude = fields.Float(digits=(10, 7), required=True)
    longitude = fields.Float(digits=(10, 7), required=True)
    radius_m = fields.Float(string='Radius (m)', default=200.0, required=True)
    alert_on_enter = fields.Boolean(default=True)
    alert_on_exit = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

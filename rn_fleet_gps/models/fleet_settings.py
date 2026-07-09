# -*- coding: utf-8 -*-
"""Company defaults for fleet GPS."""

from odoo import fields, models


class RnFleetSettings(models.Model):
    _name = 'rn.fleet.settings'
    _description = 'Fleet GPS Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    overspeed_limit = fields.Float(default=80.0, string='Overspeed Limit (km/h)')
    offline_minutes = fields.Integer(default=10)
    map_provider = fields.Selection(
        selection=[
            ('leaflet', 'Leaflet / OpenStreetMap'),
            ('google', 'Google Maps'),
        ],
        default='leaflet',
        required=True,
    )
    auto_close_trip_idle_minutes = fields.Integer(default=20)
    enable_geofence_alerts = fields.Boolean(default=True)

    _rn_fleet_settings_company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one fleet GPS settings row per company.',
    )

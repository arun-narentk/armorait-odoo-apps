# -*- coding: utf-8 -*-
"""Fleet operational alerts."""

from odoo import fields, models


class RnFleetAlert(models.Model):
    """Raised alert for speed, geofence, offline, fuel, etc."""

    _name = 'rn.fleet.alert'
    _description = 'Fleet Alert'
    _inherit = ['mail.thread']
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True, tracking=True)
    alert_type = fields.Selection(
        selection=[
            ('overspeed', 'Overspeed'),
            ('fuel_theft', 'Fuel Theft'),
            ('offline', 'Vehicle Offline'),
            ('battery', 'Battery Low'),
            ('geofence_enter', 'Geofence Entry'),
            ('geofence_exit', 'Geofence Exit'),
            ('unauthorized', 'Unauthorized Movement'),
            ('maintenance', 'Maintenance Due'),
            ('other', 'Other'),
        ],
        required=True,
        index=True,
    )
    severity = fields.Selection(
        selection=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ],
        default='warning',
        required=True,
    )
    vehicle_id = fields.Many2one('fleet.vehicle', index=True)
    device_id = fields.Many2one('rn.fleet.gps.device', index=True)
    geofence_id = fields.Many2one('rn.fleet.geofence')
    trip_id = fields.Many2one('rn.fleet.trip')
    value = fields.Float()
    threshold = fields.Float()
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('ack', 'Acknowledged'),
            ('done', 'Resolved'),
        ],
        default='open',
        tracking=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    def action_acknowledge(self):
        self.write({'state': 'ack'})
        return True

    def action_resolve(self):
        self.write({'state': 'done'})
        return True

# -*- coding: utf-8 -*-
"""GPS device registry."""

from odoo import api, fields, models


class RnFleetGpsDevice(models.Model):
    """Hardware / virtual GPS unit linked to a fleet vehicle."""

    _name = 'rn.fleet.gps.device'
    _description = 'Fleet GPS Device'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New')
    imei = fields.Char(string='IMEI', index=True)
    sim_number = fields.Char(string='SIM Number')
    firmware = fields.Char()
    provider = fields.Selection(
        selection=[
            ('manual', 'Manual / API Push'),
            ('traccar', 'Traccar'),
            ('teltonika', 'Teltonika'),
            ('gt06', 'GT06'),
            ('wialon', 'Wialon'),
            ('ruptela', 'Ruptela'),
            ('tk103', 'TK103'),
            ('other', 'Other'),
        ],
        default='manual',
        required=True,
        tracking=True,
    )
    vendor = fields.Char(string='GPS Vendor')
    install_date = fields.Date(string='Installation Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', index=True, tracking=True)
    api_url = fields.Char(string='Provider API URL')
    api_token = fields.Char(string='API Token', groups='rn_fleet_gps.group_rn_fleet_gps_manager')
    device_uid = fields.Char(string='Provider Device ID', index=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('maintenance', 'Maintenance'),
            ('retired', 'Retired'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    last_location_id = fields.Many2one('rn.fleet.gps.location', string='Last Location', copy=False)
    last_seen = fields.Datetime(related='last_location_id.timestamp', store=True)
    online = fields.Boolean(compute='_compute_online', store=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    note = fields.Text()

    @api.depends('last_seen')
    def _compute_online(self):
        now = fields.Datetime.now()
        for device in self:
            if not device.last_seen:
                device.online = False
                continue
            delta = (now - device.last_seen).total_seconds()
            device.online = delta <= 600

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.fleet.gps.device') or 'New'
        return super().create(vals_list)

    def action_activate(self):
        self.write({'state': 'active'})
        return True

    def action_test_provider(self):
        self.ensure_one()
        result = self.env['rn.fleet.gps.provider.service'].test_connection(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Fleet GPS',
                'message': result.get('message') or ('OK' if result.get('ok') else 'Failed'),
                'type': 'success' if result.get('ok') else 'warning',
                'sticky': False,
            },
        }

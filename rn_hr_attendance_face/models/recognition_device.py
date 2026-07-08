# -*- coding: utf-8 -*-
"""Trusted / blocked browser and workstation devices."""

from odoo import fields, models


class RnHrRecognitionDevice(models.Model):
    """Registers kiosk or browser devices allowed to punch attendance."""

    _name = 'rn.hr.recognition.device'
    _description = 'Face Attendance Device'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    serial_number = fields.Char(string='Serial Number', index=True)
    mac_address = fields.Char(string='MAC Address')
    browser = fields.Char()
    operating_system = fields.Char(string='Operating System')
    user_agent = fields.Text()
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('allowed', 'Allowed'),
            ('trusted', 'Trusted'),
            ('blocked', 'Blocked'),
        ],
        default='pending',
        tracking=True,
        index=True,
    )
    last_seen = fields.Datetime()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    notes = fields.Text()

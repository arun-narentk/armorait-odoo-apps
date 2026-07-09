# -*- coding: utf-8 -*-
"""Camera device registry for webcam, USB, IP, and RTSP sources."""

from odoo import fields, models


class RnHrCameraDevice(models.Model):
    """Physical or network camera used by the recognition kiosk."""

    _name = 'rn.hr.camera.device'
    _description = 'Face Attendance Camera'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    camera_type = fields.Selection(
        selection=[
            ('usb', 'USB Camera'),
            ('laptop', 'Laptop Camera'),
            ('ip', 'IP Camera'),
            ('rtsp', 'RTSP Camera'),
            ('browser', 'Browser Webcam'),
        ],
        default='browser',
        required=True,
        tracking=True,
    )
    stream_url = fields.Char(
        string='Stream URL',
        help='RTSP/IP URL when camera_type is ip or rtsp.',
    )
    device_index = fields.Integer(
        string='Device Index',
        default=0,
        help='OpenCV /dev/video index for USB or laptop cameras.',
    )
    status = fields.Selection(
        selection=[
            ('online', 'Online'),
            ('offline', 'Offline'),
            ('degraded', 'Degraded'),
            ('maintenance', 'Maintenance'),
        ],
        default='offline',
        tracking=True,
    )
    fps = fields.Float(string='FPS', digits=(16, 2))
    resolution = fields.Char(string='Resolution', default='1280x720')
    auto_reconnect = fields.Boolean(string='Reconnect Automatically', default=True)
    last_health_check = fields.Datetime(string='Last Health Check')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    location = fields.Char(string='Branch / Location')
    allowed_radius_m = fields.Float(
        string='Allowed Radius (m)',
        default=100.0,
        help='Geo fence radius used when geo validation is enabled.',
    )
    latitude = fields.Float(digits=(16, 8))
    longitude = fields.Float(digits=(16, 8))

    def action_health_check(self):
        """Run camera health probe via device/camera service (Phase 8)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Camera Health',
                'message': 'Health check will be available in Phase 8.',
                'type': 'info',
                'sticky': False,
            },
        }

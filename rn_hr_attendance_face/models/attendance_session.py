# -*- coding: utf-8 -*-
"""Kiosk attendance session (open until kiosk closes)."""

from odoo import fields, models


class RnHrAttendanceSession(models.Model):
    """Tracks an open kiosk session for a camera and company."""

    _name = 'rn.hr.attendance.session'
    _description = 'Face Attendance Kiosk Session'
    _order = 'start_at desc'

    name = fields.Char(required=True, default='Kiosk Session')
    camera_id = fields.Many2one('rn.hr.camera.device', string='Camera')
    device_id = fields.Many2one('rn.hr.recognition.device', string='Device')
    start_at = fields.Datetime(default=fields.Datetime.now)
    end_at = fields.Datetime()
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('closed', 'Closed'),
        ],
        default='open',
        index=True,
    )
    recognition_count = fields.Integer()
    success_count = fields.Integer()
    fail_count = fields.Integer()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    log_ids = fields.One2many('rn.hr.attendance.log', 'session_id', string='Logs')

    def action_close_session(self):
        """Close the kiosk session and stop accepting recognitions."""
        for session in self:
            session.write({
                'state': 'closed',
                'end_at': fields.Datetime.now(),
            })
        return True

# -*- coding: utf-8 -*-
"""Recognition attempt and attendance link log."""

from odoo import fields, models


class RnHrAttendanceLog(models.Model):
    """One recognition attempt, success or failure, optionally linked to attendance."""

    _name = 'rn.hr.attendance.log'
    _description = 'Face Attendance Recognition Log'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True, default='Recognition')
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance', ondelete='set null')
    face_id = fields.Many2one('rn.hr.employee.face', string='Face Profile', ondelete='set null')
    recognition_date = fields.Date(string='Date', default=fields.Date.context_today, index=True)
    recognition_time = fields.Datetime(string='Time', default=fields.Datetime.now, index=True)
    confidence = fields.Float(string='Confidence', digits=(16, 4))
    recognition_duration_ms = fields.Integer(string='Recognition Duration (ms)')
    device_id = fields.Many2one('rn.hr.recognition.device', string='Device')
    camera_id = fields.Many2one('rn.hr.camera.device', string='Camera')
    latitude = fields.Float(digits=(16, 8))
    longitude = fields.Float(digits=(16, 8))
    ip_address = fields.Char(string='IP Address')
    browser = fields.Char()
    operating_system = fields.Char(string='Operating System')
    image_snapshot = fields.Binary(string='Image Snapshot', attachment=True)
    recognition_result = fields.Selection(
        selection=[
            ('check_in', 'Check In'),
            ('check_out', 'Check Out'),
            ('known_face', 'Known Face'),
            ('unknown_face', 'Unknown Face'),
            ('multiple_faces', 'Multiple Faces'),
            ('spoof', 'Spoof'),
            ('low_confidence', 'Low Confidence'),
            ('no_face', 'No Face'),
            ('geo_rejected', 'Geo Rejected'),
            ('device_blocked', 'Device Blocked'),
        ],
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    session_id = fields.Many2one('rn.hr.attendance.session', string='Kiosk Session')
    notes = fields.Text()

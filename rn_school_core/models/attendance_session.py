# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolAttendanceSession(models.Model):
    _name = 'rn.school.attendance.session'
    _description = 'Attendance Session'
    _order = 'session_date desc'

    name = fields.Char(required=True)
    class_id = fields.Many2one('rn.school.class', required=True, index=True)
    session_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    method = fields.Selection(
        [('manual', 'Manual'), ('qr', 'QR Code'), ('rfid', 'RFID'), ('biometric', 'Biometric')],
        default='manual',
    )
    teacher_id = fields.Many2one('hr.employee', domain=[('is_teacher', '=', True)])
    line_ids = fields.One2many('rn.school.attendance.line', 'session_id')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

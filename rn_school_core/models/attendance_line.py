# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolAttendanceLine(models.Model):
    _name = 'rn.school.attendance.line'
    _description = 'Attendance Line'

    session_id = fields.Many2one('rn.school.attendance.session', required=True, ondelete='cascade', index=True)
    student_id = fields.Many2one('rn.school.student', required=True, index=True)
    status = fields.Selection(
        [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('leave', 'Leave')],
        default='present',
        required=True,
    )
    check_in_time = fields.Datetime()
    note = fields.Char()
    company_id = fields.Many2one(related='session_id.company_id', store=True, index=True)

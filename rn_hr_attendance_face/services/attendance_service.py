# -*- coding: utf-8 -*-
"""Create or close hr.attendance from recognition results."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrAttendanceFaceService(models.AbstractModel):
    """Maps recognition outcomes to Odoo HR attendance records."""

    _name = 'rn.hr.attendance.face.service'
    _description = 'Face Attendance Business Service'

    def process_recognition(self, employee, log_vals=None):
        """Check in or out the employee and write an attendance log."""
        employee.ensure_one()
        Attendance = self.env['hr.attendance']
        open_att = Attendance.search([
            ('employee_id', '=', employee.id),
            ('check_out', '=', False),
        ], order='check_in desc', limit=1)
        action = 'check_out' if open_att else 'check_in'
        if open_att:
            open_att.write({'check_out': fields.Datetime.now()})
            attendance = open_att
        else:
            attendance = Attendance.create({
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
            })
        vals = {
            'name': '%s %s' % (action, employee.name),
            'employee_id': employee.id,
            'attendance_id': attendance.id,
            'recognition_result': action,
            'company_id': employee.company_id.id or self.env.company.id,
        }
        if log_vals:
            vals.update(log_vals)
        log = self.env['rn.hr.attendance.log'].create(vals)
        _logger.info('Face attendance %s for employee %s log=%s', action, employee.id, log.id)
        return {
            'ok': True,
            'action': action,
            'attendance_id': attendance.id,
            'log_id': log.id,
        }

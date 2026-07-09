# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


class RnSchoolAttendanceService(models.AbstractModel):
    _name = 'rn.school.attendance.service'
    _description = 'Attendance Service'

    def create_session(self, class_id, session_date=None, method='manual'):
        school_class = self.env['rn.school.class'].browse(class_id)
        if not school_class.exists():
            raise UserError('Class not found.')
        session_date = session_date or fields.Date.context_today(self)
        session = self.env['rn.school.attendance.session'].create({
            'name': f'{school_class.name} - {session_date}',
            'class_id': school_class.id,
            'session_date': session_date,
            'method': method,
        })
        students = self.env['rn.school.student'].search([
            ('class_id', '=', school_class.id),
            ('state', '=', 'enrolled'),
        ])
        lines = []
        for student in students:
            lines.append((0, 0, {'student_id': student.id, 'status': 'present'}))
        session.write({'line_ids': lines})
        return session.id

    def mark_absent(self, session_id, student_id, note=''):
        line = self.env['rn.school.attendance.line'].search([
            ('session_id', '=', session_id),
            ('student_id', '=', student_id),
        ], limit=1)
        if line:
            line.write({'status': 'absent', 'note': note})
        settings = self.env.company._get_school_settings()
        if settings.attendance_notify_parents:
            student = self.env['rn.school.student'].browse(student_id)
            parent = student.parent_ids.filtered('is_primary')[:1]
            if parent and parent.email:
                self.env['mail.mail'].sudo().create({
                    'subject': f'Absence notice: {student.name}',
                    'body_html': f'<p>{student.name} was marked absent on {fields.Date.context_today(self)}.</p>',
                    'email_to': parent.email,
                }).send()
        return True

    def get_class_attendance_rate(self, class_id, days=30):
        from dateutil.relativedelta import relativedelta
        since = fields.Date.context_today(self) - relativedelta(days=days)
        lines = self.env['rn.school.attendance.line'].search([
            ('session_id.class_id', '=', class_id),
            ('session_id.session_date', '>=', since),
        ])
        if not lines:
            return 100.0
        present = len(lines.filtered(lambda l: l.status in ('present', 'late')))
        return round((present / len(lines)) * 100.0, 1)

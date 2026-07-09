# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolDashboardService(models.AbstractModel):
    _name = 'rn.school.dashboard.service'
    _description = 'School Dashboard Service'

    def get_principal_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        Student = self.env['rn.school.student']
        Enquiry = self.env['rn.school.admission.enquiry']
        Installment = self.env['rn.school.fee.installment']
        Session = self.env['rn.school.attendance.session']

        enrolled = Student.search_count([('company_id', '=', company_id), ('state', '=', 'enrolled')])
        enquiries = Enquiry.search_count([('company_id', '=', company_id), ('state', '=', 'new')])
        fees_due = sum(Installment.search([
            ('company_id', '=', company_id),
            ('state', 'in', ('due', 'overdue')),
        ]).mapped('net_amount'))
        sessions_today = Session.search_count([
            ('company_id', '=', company_id),
            ('session_date', '=', fields.Date.context_today(self)),
        ])
        return {
            'enrolled_students': enrolled,
            'new_enquiries': enquiries,
            'fees_outstanding': fees_due,
            'attendance_sessions_today': sessions_today,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_teacher_dashboard(self, teacher_id=None):
        teacher_id = teacher_id or self.env.user.employee_id.id
        if not teacher_id:
            return {'classes': [], 'homework_pending': 0}
        today_weekday = str(fields.Date.context_today(self).weekday())
        timetable = self.env['rn.school.timetable'].search([
            ('teacher_id', '=', teacher_id),
            ('weekday', '=', today_weekday),
        ], order='start_time')
        homework_pending = self.env['rn.school.homework.submission'].search_count([
            ('homework_id.teacher_id', '=', teacher_id),
            ('state', '=', 'submitted'),
        ])
        return {
            'teacher_name': self.env['hr.employee'].browse(teacher_id).name,
            'classes_today': [
                {'subject': t.subject, 'class': t.class_id.name, 'room': t.room or ''}
                for t in timetable
            ],
            'homework_to_grade': homework_pending,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

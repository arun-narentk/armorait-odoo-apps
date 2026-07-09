# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolHomeworkService(models.AbstractModel):
    _name = 'rn.school.homework.service'
    _description = 'Homework Service'

    def publish(self, homework_id):
        hw = self.env['rn.school.homework'].browse(homework_id)
        hw.state = 'published'
        students = self.env['rn.school.student'].search([
            ('class_id', '=', hw.class_id.id),
            ('state', '=', 'enrolled'),
        ])
        for student in students:
            self.env['rn.school.homework.submission'].create({
                'homework_id': hw.id,
                'student_id': student.id,
                'state': 'pending',
            })
        return True

    def submit(self, homework_id, student_id, note='', attachment_ids=None):
        sub = self.env['rn.school.homework.submission'].search([
            ('homework_id', '=', homework_id),
            ('student_id', '=', student_id),
        ], limit=1)
        if not sub:
            sub = self.env['rn.school.homework.submission'].create({
                'homework_id': homework_id,
                'student_id': student_id,
            })
        hw = self.env['rn.school.homework'].browse(homework_id)
        state = 'late' if fields.Datetime.now() > hw.due_date else 'submitted'
        sub.write({
            'note': note,
            'state': state,
            'submit_date': fields.Datetime.now(),
            'attachment_ids': [(6, 0, attachment_ids or [])],
        })
        return sub.id

# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolClass(models.Model):
    _name = 'rn.school.class'
    _description = 'School Class / Section'
    _order = 'grade_level, name'

    name = fields.Char(required=True, string='Class Name')
    code = fields.Char(index=True)
    grade_level = fields.Integer(string='Grade', required=True)
    section = fields.Char()
    class_teacher_id = fields.Many2one('hr.employee', domain=[('is_teacher', '=', True)])
    academic_year_id = fields.Many2one('rn.school.academic.year', required=True, index=True)
    room = fields.Char(string='Classroom')
    capacity = fields.Integer(default=40)
    student_count = fields.Integer(compute='_compute_student_count')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    def _compute_student_count(self):
        Student = self.env['rn.school.student']
        for rec in self:
            rec.student_count = Student.search_count([
                ('class_id', '=', rec.id),
                ('state', '=', 'enrolled'),
            ])

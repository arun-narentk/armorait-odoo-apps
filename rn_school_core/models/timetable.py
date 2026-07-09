# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolTimetable(models.Model):
    _name = 'rn.school.timetable'
    _description = 'Class Timetable'
    _order = 'weekday, start_time'

    name = fields.Char(required=True)
    class_id = fields.Many2one('rn.school.class', required=True, index=True)
    academic_year_id = fields.Many2one('rn.school.academic.year', required=True)
    weekday = fields.Selection(
        [
            ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
            ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'),
        ],
        required=True,
    )
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    subject = fields.Char(required=True)
    teacher_id = fields.Many2one('hr.employee', domain=[('is_teacher', '=', True)])
    room = fields.Char()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

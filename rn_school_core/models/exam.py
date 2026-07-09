# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolExam(models.Model):
    _name = 'rn.school.exam'
    _description = 'School Exam'
    _order = 'exam_date desc'

    name = fields.Char(required=True)
    academic_year_id = fields.Many2one('rn.school.academic.year', required=True, index=True)
    class_id = fields.Many2one('rn.school.class', index=True)
    subject = fields.Char(required=True)
    exam_date = fields.Date(required=True, index=True)
    max_marks = fields.Float(default=100.0)
    state = fields.Selection(
        [('scheduled', 'Scheduled'), ('marks_entry', 'Marks Entry'), ('published', 'Published')],
        default='scheduled',
    )
    result_ids = fields.One2many('rn.school.exam.result', 'exam_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

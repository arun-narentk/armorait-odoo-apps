# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolHomeworkSubmission(models.Model):
    _name = 'rn.school.homework.submission'
    _description = 'Homework Submission'
    _order = 'submit_date desc'

    homework_id = fields.Many2one('rn.school.homework', required=True, ondelete='cascade', index=True)
    student_id = fields.Many2one('rn.school.student', required=True, index=True)
    submit_date = fields.Datetime(default=fields.Datetime.now)
    note = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Submission Files')
    state = fields.Selection(
        [('pending', 'Pending'), ('submitted', 'Submitted'), ('late', 'Late'), ('graded', 'Graded')],
        default='pending',
    )
    grade = fields.Char()
    feedback = fields.Text()
    company_id = fields.Many2one(related='homework_id.company_id', store=True, index=True)

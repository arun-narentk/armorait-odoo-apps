# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSchoolExamResult(models.Model):
    _name = 'rn.school.exam.result'
    _description = 'Exam Result'
    _order = 'rank, percentage desc'

    exam_id = fields.Many2one('rn.school.exam', required=True, ondelete='cascade', index=True)
    student_id = fields.Many2one('rn.school.student', required=True, index=True)
    marks_obtained = fields.Float()
    percentage = fields.Float(compute='_compute_percentage', store=True)
    grade = fields.Char(compute='_compute_grade', store=True)
    rank = fields.Integer()
    teacher_comment = fields.Text()
    ai_comment_draft = fields.Text(string='AI Comment Draft', readonly=True)
    company_id = fields.Many2one(related='exam_id.company_id', store=True, index=True)

    @api.depends('marks_obtained', 'exam_id.max_marks')
    def _compute_percentage(self):
        for rec in self:
            max_m = rec.exam_id.max_marks or 100.0
            rec.percentage = round((rec.marks_obtained or 0) / max_m * 100.0, 2) if max_m else 0.0

    @api.depends('percentage')
    def _compute_grade(self):
        for rec in self:
            pct = rec.percentage or 0
            if pct >= 90:
                rec.grade = 'A+'
            elif pct >= 80:
                rec.grade = 'A'
            elif pct >= 70:
                rec.grade = 'B'
            elif pct >= 60:
                rec.grade = 'C'
            elif pct >= 50:
                rec.grade = 'D'
            else:
                rec.grade = 'F'

    def action_generate_ai_comment(self):
        for rec in self:
            rec.ai_comment_draft = self.env['rn.school.insight.service'].draft_report_comment(rec.id)

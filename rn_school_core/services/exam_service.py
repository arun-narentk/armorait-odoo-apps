# -*- coding: utf-8 -*-

from odoo import models


class RnSchoolExamService(models.AbstractModel):
    _name = 'rn.school.exam.service'
    _description = 'Exam Service'

    def compute_ranks(self, exam_id):
        exam = self.env['rn.school.exam'].browse(exam_id)
        results = exam.result_ids.sorted(key=lambda r: r.marks_obtained or 0, reverse=True)
        rank = 1
        for result in results:
            result.rank = rank
            rank += 1
        exam.state = 'published'
        return True

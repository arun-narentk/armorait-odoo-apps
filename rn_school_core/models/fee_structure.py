# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSchoolFeeStructure(models.Model):
    _name = 'rn.school.fee.structure'
    _description = 'Fee Structure'
    _order = 'academic_year_id desc, grade_level'

    name = fields.Char(required=True)
    academic_year_id = fields.Many2one('rn.school.academic.year', required=True, index=True)
    grade_level = fields.Integer(required=True)
    tuition_fee = fields.Float(required=True)
    transport_fee = fields.Float()
    hostel_fee = fields.Float()
    other_fee = fields.Float()
    total_fee = fields.Float(compute='_compute_total', store=True)
    installment_count = fields.Integer(default=3)
    scholarship_pct = fields.Float(string='Max Scholarship %')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('tuition_fee', 'transport_fee', 'hostel_fee', 'other_fee')
    def _compute_total(self):
        for rec in self:
            rec.total_fee = (
                (rec.tuition_fee or 0) + (rec.transport_fee or 0)
                + (rec.hostel_fee or 0) + (rec.other_fee or 0)
            )

# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolAcademicYear(models.Model):
    _name = 'rn.school.academic.year'
    _description = 'Academic Year'
    _order = 'date_start desc'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

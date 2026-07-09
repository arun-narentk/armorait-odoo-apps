# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolHomework(models.Model):
    _name = 'rn.school.homework'
    _description = 'Homework Assignment'
    _order = 'due_date desc'

    name = fields.Char(required=True)
    class_id = fields.Many2one('rn.school.class', required=True, index=True)
    teacher_id = fields.Many2one('hr.employee', domain=[('is_teacher', '=', True)])
    subject = fields.Char(required=True)
    description = fields.Html()
    due_date = fields.Datetime(required=True, index=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    submission_ids = fields.One2many('rn.school.homework.submission', 'homework_id')
    state = fields.Selection([('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed')], default='draft')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

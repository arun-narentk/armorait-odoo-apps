# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSchoolStudent(models.Model):
    _name = 'rn.school.student'
    _description = 'School Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'admission_number desc'

    name = fields.Char(required=True, tracking=True)
    admission_number = fields.Char(string='Admission No.', readonly=True, copy=False, index=True)
    roll_number = fields.Char(index=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    date_of_birth = fields.Date()
    blood_group = fields.Char()
    medical_notes = fields.Text(string='Medical Information')
    partner_id = fields.Many2one('res.partner')
    class_id = fields.Many2one('rn.school.class', string='Class', index=True)
    academic_year_id = fields.Many2one('rn.school.academic.year', index=True)
    parent_ids = fields.One2many('rn.school.parent.guardian', 'student_id')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('enrolled', 'Enrolled'),
            ('transferred', 'Transferred'),
            ('alumni', 'Alumni'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    admission_date = fields.Date()
    document_ids = fields.Many2many('ir.attachment', string='Documents')
    risk_level = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        compute='_compute_risk_level',
        store=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        ('admission_company_uniq', 'unique(admission_number, company_id)', 'Admission number must be unique per company.'),
    ]

    @api.depends('state')
    def _compute_risk_level(self):
        Insight = self.env['rn.school.insight.service']
        for student in self:
            if student.state != 'enrolled':
                student.risk_level = 'low'
                continue
            score = Insight.get_risk_score(student.id)
            if score >= 70:
                student.risk_level = 'high'
            elif score >= 40:
                student.risk_level = 'medium'
            else:
                student.risk_level = 'low'

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('admission_number'):
                vals['admission_number'] = seq.next_by_code('rn.school.student.admission') or 'ADM'
        return super().create(vals_list)

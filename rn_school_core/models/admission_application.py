# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSchoolAdmissionApplication(models.Model):
    _name = 'rn.school.admission.application'
    _description = 'Admission Application'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    enquiry_id = fields.Many2one('rn.school.admission.enquiry')
    applicant_name = fields.Char(required=True)
    parent_name = fields.Char()
    mobile = fields.Char(required=True)
    email = fields.Char()
    grade_applied = fields.Integer(string='Grade Applied')
    state = fields.Selection(
        [
            ('application', 'Application'),
            ('documents', 'Document Verification'),
            ('interview', 'Interview'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('enrolled', 'Enrolled'),
        ],
        default='application',
        required=True,
        tracking=True,
    )
    document_ids = fields.Many2many('ir.attachment', string='Submitted Documents')
    interview_notes = fields.Text()
    fee_paid = fields.Boolean()
    student_id = fields.Many2one('rn.school.student', copy=False)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.school.admission.application') or 'APP'
        return super().create(vals_list)

    def action_verify_documents(self):
        self.write({'state': 'documents'})

    def action_schedule_interview(self):
        self.write({'state': 'interview'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_create_student(self):
        self.ensure_one()
        student = self.env['rn.school.admission.service'].enroll_student(self.id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.school.student',
            'res_id': student,
            'view_mode': 'form',
            'target': 'current',
        }

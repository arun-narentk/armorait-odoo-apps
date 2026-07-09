# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


class RnSchoolAdmissionService(models.AbstractModel):
    _name = 'rn.school.admission.service'
    _description = 'Admission Service'

    def enroll_student(self, application_id, class_id=None):
        app = self.env['rn.school.admission.application'].browse(application_id)
        if not app.exists() or app.state != 'approved':
            raise UserError('Application must be approved before enrollment.')
        if app.student_id:
            return app.student_id.id
        settings = app.company_id._get_school_settings()
        student = self.env['rn.school.student'].create({
            'name': app.applicant_name,
            'academic_year_id': settings.current_academic_year_id.id,
            'class_id': class_id or False,
            'admission_date': fields.Date.context_today(self),
            'state': 'enrolled',
        })
        if app.parent_name:
            self.env['rn.school.parent.guardian'].create({
                'student_id': student.id,
                'name': app.parent_name,
                'mobile': app.mobile,
                'email': app.email,
                'is_primary': True,
            })
        app.write({'student_id': student.id, 'state': 'enrolled'})
        if student.class_id:
            self.env['rn.school.fee.service'].generate_installments(student.id)
        return student.id

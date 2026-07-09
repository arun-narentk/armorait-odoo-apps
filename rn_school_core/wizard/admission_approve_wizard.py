# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolAdmissionApproveWizard(models.TransientModel):
    _name = 'rn.school.admission.approve.wizard'
    _description = 'Approve Admission Wizard'

    application_id = fields.Many2one('rn.school.admission.application', required=True)
    class_id = fields.Many2one('rn.school.class', string='Allocate Class')
    fee_paid = fields.Boolean(string='Admission Fee Paid')

    def action_approve_enroll(self):
        self.ensure_one()
        self.application_id.write({'fee_paid': self.fee_paid, 'state': 'approved'})
        student_id = self.env['rn.school.admission.service'].enroll_student(
            self.application_id.id,
            class_id=self.class_id.id if self.class_id else False,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.school.student',
            'res_id': student_id,
            'view_mode': 'form',
            'target': 'current',
        }
